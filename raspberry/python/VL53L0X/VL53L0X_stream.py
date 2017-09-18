"""
This file streams the value of a single, directly connected sensor to the computer on the UDP_IP address on the given socket.
It does so until a keyboardInterrupt is given (Ctrl-C)
"""
import socket
import time

import VL53L0X

# Create a VL53L0X object
tof = VL53L0X.VL53L0X()

UDP_IP = "169.254.210.175"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
# Start ranging
tof.start_ranging(VL53L0X.VL53L0X_BEST_ACCURACY_MODE)
timing = tof.get_timing()
if timing < 20000:
    timing = 20000
print ("Timing %d ms" % (timing / 1000))
print ("Streaming data...")
try:
    while True:
        distance = tof.get_distance()
        if distance > 0:
            sock.sendto(str(distance), (UDP_IP, UDP_PORT))
        time.sleep(timing / 1000000.00)
except KeyboardInterrupt:
    pass
print
print("Logging done")

tof.stop_ranging()
