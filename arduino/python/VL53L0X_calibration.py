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

import VL53L0X

# Create a VL53L0X object
tof = VL53L0X.VL53L0X()

tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
print("Performing SPAD calibration")
print("Results: " + str(tof.do_spad_calibration()))
print("SPAD calibration done")
print('\n')
print("Performing REF calibration")
print("Results: " + str(tof.do_REF_calibration()))
print("REF calibration done")
print("Performing offset calibration")
distance = int(raw_input("Please give the current distance of the sensor"))
print("Results: " + str(tof.do_Offset_calibration(distance)))
print("Offset calibration done")
print("All calibrations done")

tof.stop_ranging()
