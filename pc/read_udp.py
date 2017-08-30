#!/usr/bin/python

"""
This script only works when 1 sensor is connected. Currently obsolete by read_multi_udp_blit.
"""
import socket
import matplotlib.animation as animation
import matplotlib.pyplot as plt

UDP_IP = "169.254.210.175"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

xarr = []
yarr = []
count = 0


def animate(i):
    global count
    data, addr = sock.recvfrom(64)
    distance = data
    count += 1
    xarr.append(count)
    yarr.append(distance)
    ax1.clear()
    ax1.plot(xarr, yarr)


print ("Press ctrl-c to exit")

ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()
