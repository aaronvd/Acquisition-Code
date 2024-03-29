import pyvisa as visa
import numpy as np
import time

def instrument_open(address):
    rm = visa.ResourceManager()
    instr = rm.open_resource(address)
    time.sleep(5)
    instr.read_termination = '\n'
    instr.write_termination = '\n'
    print(instr.query('*IDN?'))
    return instr

def VNA_initiate(instr, npoints, fstart, fstop, ifbw, power, calfile=None, **kwargs):
    print('Initiating VNA...\n')
    
    instr.write('SYST:PRES')   # resest VNA
    instr.write('DISP:ENAB ON') # set display to ON
    
    S_LIST = ['S11', 'S22', 'S21', 'S12']
    for i in range(4):
        instr.write('CALC:PAR:DEF:EXT "Meas{}",{}'.format(S_LIST[i],S_LIST[i]))  # define measurement for all S values
        
    if calfile is not None:
        instr.write('SENS:CORR:CSET:ACT "{}",1'.format(calfile))  # set calibration file
    instr.write('SOUR:POW1 {}'.format(power))    # set power
    instr.write('SENS:FREQ:STAR {}ghz'.format(fstart))   # set start frequency
    instr.write('SENS:FREQ:STOP {}ghz'.format(fstop))    # set stop frequency
    instr.write('SENS:SWE:POIN {}'.format(npoints))   # set number of frequency points
    instr.write('SENS:BAND {}'.format(ifbw))   # set IFBW
    time.sleep(5)
    instr.write('INIT:CONT OFF')
    instr.write('TRIG:SOUR MAN')   # set manual trigger
    instr.write('TRIG:SCOP CURR')
    instr.write('FORM:DATA ASCII,0')  # set data output format
    instr.query('*OPC?')

    time_domain = kwargs.get('time_domain', False)
    time_center = kwargs.get('time_center', 0)
    time_span = kwargs.get('time_span', 20e-9)
    if time_domain:
        for i in range(4):
            instr.write('CALC:PAR:SEL "Meas{}"'.format(S_LIST[i]))
            instr.write('CALC:TRAN:TIME:STAT ON')
            instr.write('CALC:TRAN:TIME:CENT {}'.format(time_center))
            instr.write('CALC:TRAN:TIME:SPAN {}'.format(time_span))
    window_center = kwargs.get('window_center', None)
    window_span = kwargs.get('window_span', None)
    if window_center is not None:
        for i in range(4):
            instr.write('CALC:PAR:SEL "Meas{}"'.format(S_LIST[i]))
            instr.write('CALC:FILT:GATE:TIME:CENT {}'.format(window_center))
            instr.write('CALC:FILT:GATE:TIME:SHAP NORM')
            instr.write('CALC:FILT:GATE:TIME:SPAN {}'.format(window_span))
            instr.write('CALC:FILT:GATE:TIME:TYPE BPAS')
            instr.write('CALC:FILT:GATE:TIME:STAT ON')
    
    instr.query('*OPC?')

    print('Done\n')
    if time_domain:
        return np.fromstring(instr.query('CALC:X:VAL?'), sep=",")   # return time values
    else:
        return np.fromstring(instr.query('SENS:X?'), sep=",") # return frequency values
        
def VNA_read(instr, spar):
    instr.write('CALC:PAR:SEL "Meas{}"'.format(spar))
    instr.query('*OPC?')
    instr.write('INIT:IMM')
    instr.query('*OPC?')
    instr.write('CALC:FORM IMAG')
    
    simag = np.fromstring(instr.query('CALC:DATA? FDATA'), sep=',')
    #simag = np.fromstring(instr.query('CALC:DATA? FDATA'), dtype=np.complex128, sep=',')
    instr.query('*OPC?')
    instr.write('CALC:FORM REAL')
    sreal = np.fromstring(instr.query('CALC:DATA? FDATA'), sep=',')
    #sreal = np.fromstring(instr.query('CALC:DATA? FDATA'), dtype=np.complex128, sep=',')
    
    instr.query('*OPC?')
    return sreal + 1j*simag
    








