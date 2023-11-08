import numpy as np
import sr_class as sr

ts = []
ts.append()

arduino = sr.Arduino(baudrate=115200, port='COM3')  # Update port as needed
arduino.initialize_device()