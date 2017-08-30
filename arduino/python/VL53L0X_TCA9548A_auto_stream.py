#!/usr/bin/python

# MIT License
# 
# Copyright (c) 2017 John Bryan Moore
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
import time

import VL53L0X

UDP_IP = "169.254.210.175"
UDP_PORT = 5005
MODE = VL53L0X.VL53L0X_BETTER_ACCURACY_MODE
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP


def get_connected_devices():
    print("=========================")
    print("Getting connected devices")
    print("=========================")
    connected = []
    for x in xrange(0, 7):
        tof = VL53L0X.VL53L0X(TCA9548A_Num=x, TCA9548A_Addr=0x70)
        if tof.is_connected():
            connected.append(VL53L0X.VL53L0X(TCA9548A_Num=x, TCA9548A_Addr=0x70))
    return connected


def start_ranging(devices_to_start, mode=MODE):
    print("================")
    print("Starting Devices")
    print("================")
    time.sleep(1)
    for device in devices_to_start:
        device.start_ranging(mode)


def stop_ranging(devices_to_stop):
    print("================")
    print("Stopping Devices")
    print("================")
    for device in devices_to_stop:
        device.stop_ranging()


def stream(devices_to_stream):
    string = ""
    for device in devices_to_stream:
        distance = device.get_distance()
        if distance > 0:
            string += str(distance) + " "
        else:
            string += "X"
    sock.sendto(string, (UDP_IP, UDP_PORT))


devices = get_connected_devices()
start_ranging(devices)
timing = devices[0].get_timing()
print
print("Streaming...")
print

try:
    while True:
        stream(devices)
        time.sleep(timing / 1000000.00)
except KeyboardInterrupt:
    pass

print
print("Logging done")

stop_ranging(devices)
