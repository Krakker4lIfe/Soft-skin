#!/usr/bin/python
"""
This script reads the data from the raspberry, and plots the first 2 sensors (or throws errors if there aren't).
Currently depreciated by read_multi_udp_blit.
This script doesn't use blitting for performance increase and therefore can be quite slow.
Because the recv function on line 35 is a blocking function, the graph can lag behind.

When the end of the screen is reached, the window auto rescales.
"""
import socket
import matplotlib.animation as animation
import matplotlib.pyplot as plt

UDP_IP = "169.254.210.175"  # The ip-address of the receiving pc. May need to be changed.
UDP_PORT1 = 5005  # The port that is used.

sock1 = socket.socket(socket.AF_INET,  # Internet
                      socket.SOCK_DGRAM)  # UDP
sock1.bind((UDP_IP, UDP_PORT1))

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
ax2 = fig.add_subplot(1, 1, 1)
xarr1 = []
yarr1 = []
yarr2 = []


def animate(i):
    """
    This function is responsible for the capture of data and the animation of the graph.
    :param i: simple counter
    :return: nothing
    """

    data = sock1.recv(128)
    distance = data.split(" ")

    xarr1.append(i)
    yarr1.append(distance[0])
    yarr2.append(distance[1])
    ax1.clear()
    ax2.clear()
    ax1.plot(xarr1, yarr1)
    ax2.plot(xarr1, yarr2)


print ("Press ctrl-c to exit")

ani1 = animation.FuncAnimation(fig, animate, interval=10)
plt.show()
