import numpy as np
import sr_class as sr
import time

N_sr = 2        # Number of shift registers

##### Create tuning states #####
ts = []
ts.append(np.ones((N_sr * 8), dtype=int))     # All pins on
ts.append(np.zeros((N_sr * 8), dtype=int))    # All pins off
for i in range(N_sr * 8):
    ts.append(np.zeros((N_sr * 8), dtype=int))
    ts[-1][i] = 1                           # One pin on at a time
instructions_list = []
for state in ts:
    instructions_list.append(sr.create_instruction(state))

##### Initialize Arduino #####
arduino = sr.Arduino(baudrate=115200, port='COM3')  # Update port as needed
arduino.initialize_device()

##### Apply tuning states #####
for instructions in instructions_list:
    arduino.apply_tuning_state(instructions)
    time.sleep(1)

##### Close Arduino #####
arduino.close()