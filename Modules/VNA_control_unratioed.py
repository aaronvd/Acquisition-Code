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

def VNA_initiate(instr, npoints, fstart, fstop, ifbw):
    print('Initiating VNA...\n')
    
    instr.write('SYST:PRES')   # resest VNA
    instr.write('DISP:ENAB ON') # set display to ON
    instr.write('CALC:PAR:DEF:EXT "MeasA","A,0"')  # define port 1 unratioed measurement
    instr.write('CALC:PAR:DEF:EXT "MeasB","B,0"')  # define port 2 unratioed measurement
    instr.write('SENS:FREQ:STAR {}ghz'.format(fstart))   # set start frequency
    instr.write('SENS:FREQ:STOP {}ghz'.format(fstop))    # set stop frequency
    instr.write('SENS:SWE:POIN {}'.format(npoints))   # set number of frequency points
    instr.write('SENS:BAND {}'.format(ifbw))   # set IFBW
    time.sleep(5)
    instr.write('INIT:CONT OFF')
    instr.write('TRIG:SOUR MAN')   # set manual trigger
    instr.write('TRIG:SCOP CURR')    # triggers current channel
    instr.write('FORM:DATA ASCII,0')  # set data output format
    # f = instr.query('SENS:X?')  #  return frequency values
    instr.query('*OPC?')
    
    print('Done\n')
        
def VNA_read(instr):
    instr.write('INIT:IMM')

    instr.query('*OPC?')
    instr.write('CALC:PAR:SEL "MeasA"')
    instr.query('*OPC?')
    instr.write('CALC:FORM IMAG')
    simag = np.fromstring(instr.query('CALC:DATA? FDATA'), dtype=np.complex128, sep=',')
    instr.query('*OPC?')
    instr.write('CALC:FORM REAL')
    sreal = np.fromstring(instr.query('CALC:DATA? FDATA'), dtype=np.complex128, sep=',')
    sA = sreal + 1j*simag

    instr.query('*OPC?')
    instr.write('CALC:PAR:SEL "MeasB"')
    instr.query('*OPC?')
    instr.write('CALC:FORM IMAG')
    simag = np.fromstring(instr.query('CALC:DATA? FDATA'), dtype=np.complex128, sep=',')
    instr.query('*OPC?')
    instr.write('CALC:FORM REAL')
    sreal = np.fromstring(instr.query('CALC:DATA? FDATA'), dtype=np.complex128, sep=',')
    sB = sreal + 1j*simag
    instr.query('*OPC?')

    return np.array([sA, sB]).T
    








