# Soft-skin
A soft skin for a robot. Uses distance sensors to measure deformation

Installation:
 - Install the VL53L0X port to raspbery pi with python. (https://github.com/johnbryanmoore/VL53L0X_rasp_python.git)
 - Paste the arduino/python map into the existing python map (VL53L0X_rasp_python/python)
 - Connect the raspberry via ethernet to your pc.
 - Run a python script from the pc folder on your pc.
 - Run a python script from the python folder on the arduino

 Data should be streamed from the raspberry to the pc, where it is drawn by matplotlib.