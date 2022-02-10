# =============================================================================
# TRL measurement (2 port)
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


#%% build folder for cal data using today's date
today = date.today()
date_str = today.strftime("%Y-%m-%d")
cal_folder_name = 'TRL'+date_str

root_folder = Path('/Data/2021-7-6 WR650 cal and measurements/')
meas_folder = root_folder / cal_folder_name

meas_folder.mkdir(exist_ok = True)

#%%initialize VNA

f_start = 8E9
f_stop = 12E9
f_npoints = int(251)

vna = PNA(address ='TCPIP0::10.236.73.132::inst0::INSTR')
vna.reset()
vna.scpi.set_trigger_manual
# vna.scpi.set_delete_all()
# vna.scpi.set_display_on(wnum=1,state=True)


meas_channel = 2


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

# %matplotlib qt5
#%%THRU measurement 
fig, (ax1, ax2)  = plt.subplots(2,1)

vna.sweep
#THRU S11
measurement = vna.get_measurement(mname = meas_S11)
print(f'{meas_S11} measured')
filename = meas_folder / ('THRU_' + meas_S11 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax1, label ='THRU S11')

#THRU S22
measurement = vna.get_measurement(mname = meas_S22)
print(f'{meas_S22} measured')
filename = meas_folder / ('THRU_' + meas_S22 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax2, label ='THRU S22')

#THRU S21
measurement = vna.get_measurement(mname = meas_S21)
print(f'{meas_S21} measured')
filename = meas_folder / ('THRU_' + meas_S21 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax1, label ='THRU S21')

#THRU S12
measurement = vna.get_measurement(mname = meas_S12)
print(f'{meas_S12} measured')

filename = meas_folder / ('THRU_' + meas_S12 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax2, label ='THRU S12')

#%%get switch term, should be measured with a low insertion loss (i.e. with thru measurement should work)
switch_terms = vna.get_switch_terms()

filename = meas_folder / ('SWITCH_TERMS.ntwk')
rf.write(str(filename), switch_terms)

#%%REFLECT measurement 
vna.sweep

#REFLECT S11
measurement = vna.get_measurement(mname = meas_S11)
print(f'{meas_S11} measured')
filename = meas_folder / ('REFLECT_' + meas_S11 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax1, label ='REFLECT S11')

#REFLECT S21
measurement = vna.get_measurement(mname = meas_S21)
print(f'{meas_S21} measured')
filename = meas_folder / ('REFLECT_' + meas_S21 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax1, label ='REFLECT S21')

#%%
vna.sweep

#REFLECT S22
measurement = vna.get_measurement(mname = meas_S22)
print(f'{meas_S22} measured')
filename = meas_folder / ('REFLECT_' + meas_S22 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax2, label ='REFLECT S22')

#REFLECT S12
measurement = vna.get_measurement(mname = meas_S12)
print(f'{meas_S12} measured')

filename = meas_folder / ('REFLECT_' + meas_S12 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax2, label ='REFLECT S12')

#%%LINE measurement 

vna.sweep
#LINE S11
measurement = vna.get_measurement(mname = meas_S11)
print(f'{meas_S11} measured')
filename = meas_folder / ('LINE_' + meas_S11 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax1, label ='LINE S11')

#THRU S21
measurement = vna.get_measurement(mname = meas_S21)
print(f'{meas_S21} measured')
filename = meas_folder / ('LINE_' + meas_S21 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax1, label ='LINE S21')

#LINE S22
measurement = vna.get_measurement(mname = meas_S22)
print(f'{meas_S22} measured')
filename = meas_folder / ('LINE_' + meas_S22 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax2, label ='LINE S22')

#LINE S12
measurement = vna.get_measurement(mname = meas_S12)
print(f'{meas_S12} measured')

filename = meas_folder / ('LINE_' + meas_S12 + '.ntwk')
rf.write(str(filename), measurement)
measurement.frequency.units = 'ghz'
measurement.plot_s_db(ax = ax2, label ='LINE S12')



