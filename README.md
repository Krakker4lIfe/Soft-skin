# Soft-skin
This repository contains the code for getting measurement data from (multiple) VL53L0X or VL6180X devices and is heavily based on other repositories.
The distance sensor data was originally intended for use in a soft skin for robots.

Installation:
 - Install the VL53L0X port to raspbery pi with python. (https://github.com/johnbryanmoore/VL53L0X_rasp_python.git)
 - Paste the arduino/python map into the existing python map (VL53L0X_rasp_python/python)
 - Run a python script from the python folder on the raspberry pi
 

If you want the data streamed to your pc.
- Connect your pc to the raspberry (ethernet or wireless)
- Make sure the IP address and port are correct.
- Run a stream progam on the raspberry pi
- Run the correct reading program on the pc. (preferably read_multi_udp_blit.py)
