# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 17:51:54 2021

@author: Zaber
"""
# =============================================================================
# 12-element calibration on 2 port DUT
# =============================================================================


import skrf as rf
from skrf.vi.vna import PNA
from skrf import Network
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import date

rf.stylely()
# %matplotlib inline
#sweep values

#%%initialize VNA

f_start = 8E9
f_stop = 12E9
f_npoints = int(101)

vna = PNA(address ='TCPIP0::10.236.73.132::inst0::INSTR')
vna.reset()
vna.scpi.set_trigger_manual
# vna.scpi.set_delete_all()
# vna.scpi.set_display_on(wnum=1,state=True)


meas_channel = 2

fig, (ax1, ax2)  = plt.subplots(2,1)

meas_S11 = 'S11'
vna.create_meas(meas_S11,'S11', channel = meas_channel) 
meas_S22 = 'S22'
vna.create_meas(meas_S22,'S22', channel = meas_channel) 
meas_S21 = 'S21'
vna.create_meas(meas_S21,'S21', channel = meas_channel) 
meas_S12 = 'S12'
vna.create_meas(meas_S12,'S12', channel = meas_channel) 

vna.set_frequency_sweep(f_start, 
                        f_stop, 
                        f_npoints, 
                        f_unit = 'Hz',
                        channel = meas_channel, 
                        )


#%%
vna.sweep

measurement_S11 = vna.get_measurement(mname = meas_S11)
measurement_S22 = vna.get_measurement(mname = meas_S22)
measurement_S21 = vna.get_measurement(mname = meas_S21)
measurement_S12 = vna.get_measurement(mname = meas_S12)


measurement = rf.two_port_reflect(measurement_S11, measurement_S22)
measurement.s[:,0,1] = measurement_S12.s[:,0,0]
measurement.s[:,1,0] = measurement_S21.s[:,0,0]

#%%
measurement_corrected = cal.apply_cal(measurement)

#%% plot
# %matplotlib qt5

fig, (ax1, ax2)  = plt.subplots(2,1)
measurement.plot_s_deg(ax = ax1)
#measurement_corrected.plot_s_deg(ax = ax2)


#%% build folder for cal data using today's date
today = date.today()
date_str = today.strftime("%Y-%m-%d")
cal_folder_name = 'test_measurements'+date_str

root_folder = Path('/Users/Zaber/Documents/data/scikit_measurements/')
meas_folder = root_folder / cal_folder_name

meas_folder.mkdir(exist_ok = True)

#%%save measurement
measurement_name = 's_parameter_two_port'

filename = meas_folder / (measurement_name + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_mag(ax = ax1, label ='Short S11')





