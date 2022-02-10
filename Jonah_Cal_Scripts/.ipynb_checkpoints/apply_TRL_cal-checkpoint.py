#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 11:55:27 2021

@author: jgollub
"""

import numpy as np
from pathlib import Path
import skrf as rf
from skrf.calibration import OnePort
from cycler import cycler


import matplotlib.pyplot as plt
rf.stylely

# %matplotlib inline
## created calibration class using 

plt.rcParams['axes.prop_cycle'] = cycler(color=['b', 'r', 'g', 'y'])
# plt.rcParams['axes.prop_cycle'] = cycler(color=[.1, , 'r', 'y'])

#%% Measured response from TRL Cal 

cal_folder_name = 'TRL2021-04-12'

measurement_root_folder = Path('/Users/Zaber/Documents/data/scikit_measurements/')
meas_folder = measurement_root_folder / cal_folder_name

THRU_S11 = np.load(meas_folder / 'THRU_S11.ntwk', allow_pickle = True)
THRU_S22 = np.load(meas_folder / 'THRU_S22.ntwk', allow_pickle = True)
THRU_S21 = np.load(meas_folder / 'THRU_S21.ntwk', allow_pickle = True)
THRU_S12 = np.load(meas_folder / 'THRU_S12.ntwk', allow_pickle = True)

REFLECT_S11 = np.load(meas_folder / 'REFLECT_S11.ntwk', allow_pickle = True)
REFLECT_S22 = np.load(meas_folder / 'REFLECT_S22.ntwk', allow_pickle = True)
REFLECT_S21 = np.load(meas_folder / 'REFLECT_S21.ntwk', allow_pickle = True)
REFLECT_S12 = np.load(meas_folder / 'REFLECT_S12.ntwk', allow_pickle = True)

LINE_S11 = np.load(meas_folder / 'LINE_S11.ntwk', allow_pickle = True)
LINE_S22 = np.load(meas_folder / 'LINE_S22.ntwk', allow_pickle = True)
LINE_S21 = np.load(meas_folder / 'LINE_S21.ntwk', allow_pickle = True)
LINE_S12 = np.load(meas_folder / 'LINE_S12.ntwk', allow_pickle = True)

SWITCH_TERMS = np.load(meas_folder / 'SWITCH_TERM.ntwk', allow_pickle = True)

THRU = rf.two_port_reflect(THRU_S11, THRU_S22)
n_freq = len(THRU.f)
pad_zeros = np.zeros((n_freq, 2, 2)) 

THRU.s[:,0,1] = THRU_S12.s[:,0,0]
THRU.s[:,1,0] = THRU_S21.s[:,0,0]
THRU.z0  = (50+0j)*np.ones((n_freq, 4)) 


REFLECT = rf.two_port_reflect(REFLECT_S11, REFLECT_S22)
REFLECT.s[:,0,1] = REFLECT_S12.s[:,0,0]
REFLECT.s[:,1,0] = REFLECT_S21.s[:,0,0]
REFLECT.z0 = (50+0j)*np.ones((n_freq, 4))

LINE = rf.two_port_reflect(LINE_S11, LINE_S22)
LINE.s[:,0,1] = LINE_S12.s[:,0,0]
LINE.s[:,1,0] = LINE_S21.s[:,0,0]
LINE.z0 = (50+0j)*np.ones((n_freq, 4))

my_ideals = [None, -1, None]

my_measured = [\
               THRU,
               REFLECT,
               LINE,
        ]
    

#%%
    
    
## create a Calibration instance
trl = rf.TRL(\
        measured = my_measured,
        ideals = my_ideals,
        estimate_line = True,
        switch_terms = SWITCH_TERMS,
        )

# run calibration algorithm
trl.run()
# trl_8.run()
# trl=trl_8.coefs_12term()


#%%
# apply it to a dut
dut_raw = LINE
dut_raw.name = 'test'
dut_corrected = trl.apply_cal(dut_raw)
dut_corrected.name =  dut_raw.name + 'corrected'

# plot results
fig, (ax1,ax2)= plt.subplots(2,1)
dut_corrected.frequency.unit = 'ghz'

dut_corrected.plot_s_deg(ax = ax1)
dut_corrected.plot_s_db(ax = ax2)

# save results
dut_corrected.write_touchstone()

#%%
# rf.Network(SHORT_S11.as_posix())
