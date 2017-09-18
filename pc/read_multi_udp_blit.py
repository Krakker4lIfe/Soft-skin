#!/usr/bin/python
"""
This script reads the data from the raspberry, auto detects the number of sensors that are streamed, and plots all of them.
This script uses blitting for performance increase.
It also adds  the filtered values of all sensors. This is an exponential moving average. (see https://github.com/dxinteractive/ResponsiveAnalogRead)
Can be enabled and disabled with a button, no performance increase as the filter is calculated all the time.
The window settings however are fixed. When the end of the screen is reached, the window resets. This is to keep performance high, for drawing multiple lines.

"""
import socket

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

UDP_IP = "169.254.210.175"  # The ip address of the receiving pc. May need to be changed
UDP_PORT1 = 5005  # The port that is used


class Filter:
    """
    This class is for calculating the filter value of the sensor value
    For each sensor, a filter instance is created and and filter values are updated.
    """

    def __init__(self):
        # Setting: Whether or not to enable sleep mode. In this mode, the filter is a bit less responsive to the changes. This is to block out noise
        self.sleepEnable = True
        # Setting: The threshold for waking up - exiting sleep mode.
        self.activityThreshold = 2.5
        # The max value of the sensor
        self.analogResolution = 100.0
        # No setting, the error
        self.errorEMA = 0.0
        # No setting: whether or not the filter is currently in sleep mode
        self.sleeping = False
        # Setting: The amount of 'snap' of the filter. If too loose, the filter is not following well. If to high, overly compensating.
        self.snapMultiplier = 0.5
        # No setting: the current filter value
        self.smoothValue = 0.0
        # Setting: Whether to enable edge snapping. This makes it easier to get to the edges( min/max) of the measurement values.
        self.snapEnable = False

    def filter_value(self, new_value):
        """
        Function responsible for updating the filter. Returns the new filtered value.
        :param new_value: The current measurement data
        :return: The new filtered value
        """
        # if sleep and edge snap are enabled and the new value is very close to an edge, drag it a little closer to the edges
        #  This'll make it easier to pull the output values right to the extremes without sleeping,
        #  and it'll make movements right near the edge appear larger, making it easier to wake up
        if self.sleepEnable and self.snapEnable:
            if new_value < self.activityThreshold:
                new_value = (new_value * 2) - self.activityThreshold
            elif new_value > self.analogResolution - self.activityThreshold:
                new_value = (new_value * 2) - self.analogResolution + self.activityThreshold

        # get difference between new input value and current smooth value
        diff = abs(new_value - self.smoothValue)

        # measure the difference between the new value and current value
        # and use another exponential moving average to work out what
        # the current margin of error is
        self.errorEMA += ((new_value - self.smoothValue) - self.errorEMA) * 0.4

        # if sleep has been enabled, sleep when the amount of error is below the activity threshold
        if self.sleepEnable:
            # recalculate sleeping status
            self.sleeping = abs(self.errorEMA) < self.activityThreshold

        # if we're allowed to sleep, and we're sleeping
        # then don't update responsiveValue this loop
        # just output the existing responsiveValue
        if self.sleepEnable and self.sleeping:
            return int(self.smoothValue)

            #  use a 'snap curve' function, where we pass in the diff (x) and get back a number from 0-1.
            #  We want small values of x to result in an output close to zero, so when the smooth value is close to the input value
            #  it'll smooth out noise aggressively by responding slowly to sudden changes.
            #  We want a small increase in x to result in a much higher output value, so medium and large movements are snappy and responsive,
            #  and aren't made sluggish by unnecessarily filtering out noise. A hyperbola (f(x) = 1/x) curve is used.
            #  First x has an offset of 1 applied, so x = 0 now results in a value of 1 from the hyperbola function.
            #  High values of x tend toward 0, but we want an output that begins at 0 and tends toward 1, so 1-y flips this up the right way.
            #  Finally the result is multiplied by 2 and capped at a maximum of one, which means that at a certain point all larger movements are maximally snappy
            #
            #  then multiply the input by SNAP_MULTIPLIER so input values fit the snap curve better.
        snap = snap_curve(diff * self.snapMultiplier)

        #  when sleep is enabled, the emphasis is stopping on a responsiveValue quickly, and it's less about easing into position.
        #  If sleep is enabled, add a small amount to snap so it'll tend to snap into a more accurate position before sleeping starts.
        if self.sleepEnable:
            snap *= 0.5 + 0.5

            # // calculate the exponential moving average based on the snap
        self.smoothValue += (new_value - self.smoothValue) * snap

        # // ensure output is in bounds
        if self.smoothValue < 0.0:
            self.smoothValue = 0.0
        elif self.smoothValue > self.analogResolution - 1:
            self.smoothValue = self.analogResolution - 1

            # expected output is an integer
        return int(self.smoothValue)


def animate(i):
    """
    This is the animation function for the window.
    It receives the data, appends it to the data for the plotting and calculates the filter values.
    :param i:
    :return:
    """
    global count
    data = sock1.recv(32)
    distance = data.split(" ")
    distance.pop()  # The last one is always empty
    for x in range(len(distance)):
        try:
            distance.append(filters[x].filter_value(int(distance[x])))  # Calculate filter values
        except ValueError:
            distance.append(0)  # This means an error occurred and a value X was transmitted
    if count >= ax.get_xlim()[1]:  # Meaning the data has overflowed the window in the x direction
        count = 0
        for sensor in range(nbSensors * 2):
            del ydata[sensor][:]
        del xdata[:]
    xdata.append(count)
    for sensor in range(len(line)):
        try:
            ydata[sensor].append(int(distance[sensor]))
        except (ValueError, IndexError):
            ydata[sensor].append(0)

        line[sensor].set_data(xdata, ydata[sensor])
    count += 1
    return line


# Init only required for blitting to give a clean slate.
def init():
    ax.set_xlim(0, 100)
    ax.set_ylim(20, 100)
    for sensor in range(len(line)):
        line[sensor].set_data(xdata, ydata[sensor])
    return line


def get_nb_sensors():
    """
    Receives a packet on the standard bus, and deduces the number of sensors streaming to this device.
    :return: The number of sensors
    """
    data = sock1.recv(32)  # Argument is buffer length. May be increased when more than 4 sensors are connected.
    distance = data.split(" ")  # The data is a string of values, separated by a space.
    return len(distance) - 1


def snap_curve(x):
    """
    The snap curve function. This fuction is used in the filter_value function. More info there.
    :param x: The difference between the measured value and the previous filter value
    :return: A coefficient for the amount of snap.
    """
    y = 1.0 / (x + 1.0)
    y = (1.0 - y) * 2.0
    if y > 1.0:
        return 1.0

    return y


def toggle_filter(event):
    for fil in range(nbSensors, 2 * nbSensors):
        line[fil].set_visible(not line[fil].get_visible())


# The socket to listen on
sock1 = socket.socket(socket.AF_INET,  # Internet
                      socket.SOCK_DGRAM)  # UDP
sock1.bind((UDP_IP, UDP_PORT1))

fig, ax = plt.subplots()

nbSensors = get_nb_sensors()
filter_on = False
filters = [Filter() for x in range(nbSensors)]
# Initialize all plotting data
xdata = []
ydata = [[] for x in range(nbSensors * 2)]
line = []
for sensor in range(nbSensors * 2):
    cur_line, = ax.plot(xdata, ydata[sensor])
    line.append(cur_line)

# Setting the axes
ax.set_xlabel('Aantal metingen')
ax.set_ylabel('Afstand [mm]')
rax = plt.axes([0.7, 0.01, 0.1, 0.05])  # x start, y start, width, height
button_filter = Button(rax, 'Filters')
button_filter.on_clicked(toggle_filter)

count = 0
# The animation function
ani = animation.FuncAnimation(fig, animate, init_func=init,
                              interval=0, blit=True)
# This is a blocking function. This keeps showing the plot until the plot is closed.
plt.show()
