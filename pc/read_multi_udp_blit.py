#!/usr/bin/python
"""
This script reads the data from the raspberry, auto detects the number of sensors that are streamed, and plots all of them.
This script uses blitting for performance increase.
The window settings however are fixed. When the end of the screen is reached, the window resets. This is to keep performance high, for drawing multiple lines.

"""
import socket

import matplotlib.animation as animation
import matplotlib.pyplot as plt

UDP_IP = "169.254.210.175"  # The ip address of the receiving pc. May need to be changed
UDP_PORT1 = 5005  # The port that is used


def animate(i):
    global count
    data = sock1.recv(32)
    distance = data.split(" ")
    if count >= ax.get_xlim()[1]:
        count = 0
        for sensor in xrange(nbSensors):
            ydata[sensor].__delslice__(0, ydata[sensor].__sizeof__())
        xdata.__delslice__(0, xdata.__sizeof__())
    xdata.append(count)
    for sensor in xrange(nbSensors):
        try:
            ydata[sensor].append(int(distance[sensor]))
        except ValueError:
            ydata[sensor].append(0)
        line[sensor].set_data(xdata, ydata[sensor])
    count += 1
    return line


# Init only required for blitting to give a clean slate.
def init():
    ax.set_xlim(0, 100)
    ax.set_ylim(20, 100)
    for sensor in xrange(nbSensors):
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


sock1 = socket.socket(socket.AF_INET,  # Internet
                      socket.SOCK_DGRAM)  # UDP
sock1.bind((UDP_IP, UDP_PORT1))

fig, ax = plt.subplots()

nbSensors = get_nb_sensors()
xdata = []
ydata = [[] for x in xrange(nbSensors)]
line = []
for sensor in xrange(nbSensors):
    cur_line, = ax.plot(xdata, ydata[sensor])
    line.append(cur_line)

ax.set_xlabel('Aantal metingen')
ax.set_ylabel('Afstand [mm]')
count = 0

ani = animation.FuncAnimation(fig, animate, init_func=init,
                              interval=0, blit=True)
plt.show()
