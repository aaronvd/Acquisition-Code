#%%####################################
 
 # Import modules

#######################################
import sys
sys.path.append(r'C:\Users\smithlab\Documents\Acquisition-Code\Modules')
import pin_mappings as pm
import numpy as np
import numpy.matlib
import mainPyDAC2_module_multiple as tune
import time
import scipy.io

#%%####################################
 
 # Load/make tuning states

#######################################
mat = scipy.io.loadmat(r'C:\Users\smithlab\Documents\Aaron\Tuning States\steering_test_22-06-08.mat')
element_voltages = mat['ts']

ts = pm.make_ts_quickturn(element_voltages)

#%%####################################
 
 # Initialize Arduinos

#######################################
numDACs = 30
serial1 = tune.initializeArduino(numDACs, "COM9")
serial2 = tune.initializeArduino(numDACs, "COM10")

#%%####################################
 
 # Tune

#######################################
indx = 0

tune.testProgram30DAC(serial1,ts[indx])
tune.testProgram30DAC(serial2,ts[indx])
time.sleep(0.01)








