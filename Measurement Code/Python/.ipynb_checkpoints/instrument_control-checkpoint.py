import pyvisa as visa
import time

def instrument_open(address):
    rm = pyvisa.ResourceManager()
    instr = rm.open_resource(address)
    time.sleep(5)
    instr.read_termination = '\n'
    instr.write_termination = '\n'
    print(instr.query('*IDN?'))
    return instr

def VNA_initiate(instr, npoints, fstart, fstop, ifbw, power, spar, calfile=None):
    print('Initiating VNA...\n')
    
    instr.write('SYST:PRES')   # resest VNA
    instr.write('DISP:ENAB ON') # set display to ON
    instr.write('CALC:PAR:DEF:EXT "Meas{}",{}'.format(spar,spar))  # define measurement
    if calfile is not None:
        instr.write('SENS:CORR:CSET:ACT "{}",1'.format(calfile))  # set calibration file
    instr.write('SOUR:POW1 {}'.format(power))    # set power
    instr.write('SENS:FREQ:STAR {}hz'.format(fstart))   # set start frequency
    instr.write('SENS:FREQ:STOP {}hz'.format(fstop))    # set stop frequency
    instr.write('SENS:SWE:POIN {}'.format(npoints))   # set number of frequency points
    instr.write('SENS:BAND {}'.format(ifbw))   # set IFBW
    instr.write('INIT:CONT OFF')
    instr.write('TRIG:SOUR MAN')   # set manual trigger
    instr.write('TRIG:SCOP CURR')
    instr.write('FORM:DATA ASCII,0')  # set data output format
    instr.query('SENS:X?')
    instr.query('*OPC?')
    
    print('Done\n')
    
def VNA_read(instr, spar):
    instr.write('CALC:PAR:SEL "Meas{}"'.format(spar))
    instr.query('*OPC?')
    instr.write('INIT:IMM')
    instr.query('*OPC?')
    instr.write('CALC:FORM IMAG')
    simag = instr.query('CALC:DATA? FDATA')
    instr.query('*OPC?')
    instr.write('CALC:FORM REAL')
    sreal = instr.query('CALC:DATA? FDATA')
    instr.query('*OPC?')
    return sreal + 1j*simag
    








