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
"""
This file contains the VL53L0x object the others reference to. It is the bridge between python and C.
It also contains some calibration functions. For more information of the ST library, see the documentation:
http://www.st.com/en/embedded-software/stsw-img005.html
"""
import os
import sys
from ctypes import *
import smbus

VL53L0X_GOOD_ACCURACY_MODE = 0  # Good Accuracy mode
VL53L0X_BETTER_ACCURACY_MODE = 1  # Better Accuracy mode
VL53L0X_BEST_ACCURACY_MODE = 2  # Best Accuracy mode
VL53L0X_LONG_RANGE_MODE = 3  # Long Range mode
VL53L0X_HIGH_SPEED_MODE = 4  # High Speed mode

i2cbus = smbus.SMBus(1)


# i2c bus read callback
def i2c_read(address, reg, data_p, length):
    """
    This i2c read function for the entire ST library. Each function of the ST library uses this function to communicate with the VL53L0x chip.
    Currently uses the smbus library for i2c communication.

    :param address: The address of the device
    :param reg: The registry address in the device
    :param data_p: The data
    :param length: The length of the data
    :return: The return value. See implementation
    """
    ret_val = 0
    result = []

    try:
        result = i2cbus.read_i2c_block_data(address, reg, length)
    except IOError:
        ret_val = -1

    if ret_val == 0:
        for index in range(length):
            data_p[index] = result[index]

    return ret_val


# i2c bus write callback
def i2c_write(address, reg, data_p, length):
    """
    This i2c write function for the entire ST library. Each function of the ST library uses this function to communicate with the VL53L0x chip.
    Currently uses the smbus library for i2c communication.

    :param address: The address of the device
    :param reg: The registry address in the device
    :param data_p: The data
    :param length: The length of the data
    :return: The return value. See implementation
    """
    ret_val = 0
    data = []

    for index in range(length):
        data.append(data_p[index])
    try:
        i2cbus.write_i2c_block_data(address, reg, data)
    except IOError:
        ret_val = -1

    return ret_val


# Load VL53L0X shared lib
tof_lib = CDLL("../bin/vl53l0x_python.so")

# Create read function pointer
READFUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
read_func = READFUNC(i2c_read)

# Create write function pointer
WRITEFUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
write_func = WRITEFUNC(i2c_write)

# pass i2c read and write function pointers to VL53L0X library
tof_lib.VL53L0X_set_i2c(read_func, write_func)


class VL53L0X(object):
    """VL53L0X ToF."""

    object_number = 0

    def __init__(self, address=0x29, TCA9548A_Num=255, TCA9548A_Addr=0, **kwargs):
        """Initialize the VL53L0X ToF Sensor from ST"""
        self.device_address = address
        self.TCA9548A_Device = TCA9548A_Num
        self.TCA9548A_Address = TCA9548A_Addr
        self.my_object_number = VL53L0X.object_number
        VL53L0X.object_number += 1

    def start_ranging(self, mode=VL53L0X_GOOD_ACCURACY_MODE):
        """Start VL53L0X ToF Sensor Ranging"""
        tof_lib.startRanging(self.my_object_number, mode, self.device_address, self.TCA9548A_Device, self.TCA9548A_Address)

    def stop_ranging(self):
        """Stop VL53L0X ToF Sensor Ranging"""
        tof_lib.stopRanging(self.my_object_number)

    def get_distance(self):
        """Get distance from VL53L0X ToF Sensor"""
        return tof_lib.getDistance(self.my_object_number)

    # This function included to show how to access the ST library directly
    # from python instead of through the simplified interface
    def get_timing(self):
        dev = tof_lib.getDev(self.my_object_number)
        budget = c_uint(0)
        budget_p = pointer(budget)
        status = tof_lib.VL53L0X_GetMeasurementTimingBudgetMicroSeconds(dev, budget_p)
        if status == 0:
            return budget.value + 1000
        else:
            return 0

    def do_spad_calibration(self):
        """
        Custom function. Performs SPAD calibration of the sensor.
        This function accesses the ST library directly.
        :return: The status
        """
        print ("Performing SPAD calibration")
        dev = tof_lib.getDev(self.my_object_number)
        spad_count = c_uint(0)
        p_spad_count = pointer(spad_count)
        is_aperture_spads = c_uint(0)
        p_is_aperture_spads = pointer(is_aperture_spads)
        status = tof_lib.VL53L0X_PerformRefSpadManagement(dev, p_spad_count, p_is_aperture_spads)
        if status == 0:
            return "SpadCount: " + str(spad_count.value) + " IsApertureSpads: " + str(is_aperture_spads.value)
        return str(status)

    def get_SPAD_params(self):
        """
        Custom function. Returns current SPAD parameters of the sensor.
        This function accesses the ST library directly.
        :return: The status
        """
        print ("Getting SPAD settings")
        Dev = tof_lib.getDev(self.my_object_number)
        SpadCount = c_uint(0)
        pSpadCount = pointer(SpadCount)
        IsApertureSpads = c_uint(0)
        pIsApertureSpads = pointer(IsApertureSpads)
        status = tof_lib.VL53L0X_GetReferenceSpads(Dev, pSpadCount, pIsApertureSpads)
        if status == 0:
            return "SpadCount: " + str(SpadCount.value) + " IsApertureSpads: " + str(IsApertureSpads.value)
        return str(status)

    def do_REF_calibration(self):
        """
        Custom function. Performs a REF calibration of the sensor.
        This function accesses the ST library directly.
        :return: The status
        """
        print ("Performing REF calibration")
        Dev = tof_lib.getDev(self.my_object_number)
        VhvSettings = c_uint(0)
        pVhvSettings = pointer(VhvSettings)
        PhaseCal = c_uint(0)
        pPhaseCal = pointer(PhaseCal)
        status = tof_lib.VL53L0X_PerformRefCalibration(Dev, pVhvSettings, pPhaseCal)
        if status == 0:
            return "VhvSettings: " + str(VhvSettings.value) + " PhaseCal: " + str(PhaseCal.value)
        return str(status)

    def do_Offset_calibration(self, distanceInMm=100):
        print ("Performing Offset Calibration")
        Dev = tof_lib.getDev(self.my_object_number)
        distance = c_uint(distanceInMm << 16)
        Offset = c_uint(0)
        pOffset = pointer(Offset)
        Status = tof_lib.VL53L0X_PerformOffsetCalibration(Dev, distance, pOffset)
        if Status == 0:
            return "Offset: " + str(Offset.value)
        return "Error"

    def do_XTalk_calibration(self, distanceInMm=500):
        print ("Performing XTalk Calibration")
        Dev = tof_lib.getDev(self.my_object_number)
        distance = c_uint(distanceInMm << 16)
        CompRate = c_uint(0)
        pCompRate = pointer(CompRate)
        Status = tof_lib.VL53L0X_PerformXTalkCalibration(Dev, distance, pCompRate)
        if Status == 0:
            return "XTalk Compensation Rate: " + str(CompRate.value)
        return "Error"

    def change_Address(self, address=0x29):
        print ("Changing device address to " + str(address))
        Dev = tof_lib.getDev(self.my_object_number)
        cAddress = c_uint(address)
        Status = tof_lib.VL53L0X_SetDeviceAddress(Dev, cAddress)
        if (Status == 0):
            return "Changed device address to " + str(address)
        return "Error"

    def is_connected(self):
        """
        Custom function used for auto detection in the VL53L0X_TCA9548A_auto_stream script.
        Still prints a lot of data from the python library.
        :return: False if this sensor is not connected, True if connected.
        """
        sys.stdout = os.devnull
        self.start_ranging()
        if self.get_timing() == 0:
            flag = False
        else:
            flag = True
        self.stop_ranging()
        sys.stdout = sys.__stdout__
        return flag
