#!/usr/bin/python

"""
 This file detect all the sensors that are connected to the TCA9548A on the i2c address 0x70 and streams their data to the pc.
 """

import socket
import sys
from time import sleep
import VL6180X

"""-- Setup --"""
debug = False  # Enable this if you want all the debug information of the sensor printed on your command window

info = False  # Enable this if you want just a bit of information about which sensors are found on the TC.
UDP_IP = "169.254.210.175"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)
tc_i2c_address = 0x70
sensor_i2c_address = 0x29
if len(sys.argv) > 1:
    if sys.argv[1] == "debug":  # sys.argv[0] is the filename
        debug = True
        info = True
if len(sys.argv) > 1:
    if sys.argv[1] == "info":  # sys.argv[0] is the filename
        info = True
sensors = []
# setup ToF ranging/ALS sensor
for i in range(8):
    sensor = VL6180X.return_sensor_if_connected(tc_i2c_address, i, sensor_i2c_address, True, debug=debug)
    if sensor is not None:
        if info:
            print("Found sensor on:")
            print("\tMultiplexer address: {}".format(tc_i2c_address))
            print("\tSensor address: {}".format(sensor_i2c_address))
            print("\tMultiplexer device: {}".format(i))
        sensor.get_identification()
        if info:
            if sensor.idModel != 0xB4:
                print("\tNot a valid sensor id: %X" % sensor.idModel)
            else:
                print("\tSensor model: %X" % sensor.idModel)
                print("\tSensor model rev.: %d.%d" % (sensor.idModelRevMajor, sensor.idModelRevMinor))
                print("\tSensor module rev.: %d.%d" % (sensor.idModuleRevMajor, sensor.idModuleRevMinor))
                print("\tSensor date/time: %X/%X" % (sensor.idDate, sensor.idTime))
        sensor.default_settings()
        sensors.append(sensor)

print()
print("Streaming...")
print()
"""-- MAIN LOOP --"""
try:
    while True:
        string = ""
        for sensor in sensors:
            try:
                distance = sensor.get_distance()
                string += str(distance) + " "
            except IOError:
                string += "X "
        sock.sendto(string, (UDP_IP, UDP_PORT))
        print(string)
        sleep(1)
except KeyboardInterrupt:
    pass

print()
print("Logging done")
