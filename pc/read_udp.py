#!/usr/bin/python

# MIT License
#
# Copyright (c) 2017 John Bryan Moore, Sampath Vanimisetti
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
