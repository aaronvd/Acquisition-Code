import pyvisa as visa
import numpy as np

def instrument_open(address):
    rm = visa.ResourceManager()
    inst = rm.open_resource(address)
    inst.timeout = 20000
    # time.sleep(5)
    inst.read_termination = '\n'
    inst.write_termination = '\n'
    print(inst.query('*IDN?'))
    inst.write('*CLS')    # clear status
    inst.write("*RST")     # Load the default setup
    return inst

def scope_initialize(inst, channels=[1,2], N_points=10000, duration=1E-3, **kwargs):
    for c in channels:
        inst.write(':CHANnel{}:PROBe {}'.format(c, kwargs.get('attenuation', 1.0)))   # set probe attenuation
    inst.write(':AUToscale')
    inst.write(':TRIGger:MODE EDGE')
    inst.write(':TIMebase:RANGe {}'.format(duration))
    inst.write(':ACQuire:POINts {}'.format(N_points))
    inst.write(':ACQuire:INTerpolate OFF')
    inst.write(':WAVeform:STReaming OFF')
    # inst.write(':WMEM:TIETimebase ON')
    inst.query('*OPC?')
    
def scope_read(inst, channel=1):
    inst.write(':MEASure:SOURce CHANnel{}'.format(channel))
    inst.write(':WAVeform:SOURce CHANnel{}'.format(channel))
    inst.query('*OPC?')
    inst.write(':WAV:FORM ASCii')
    x_increment = float(inst.query(':WAVeform:XINCrement?'))
    x_origin = float(inst.query(':WAVeform:XORigin?'))
    y_increment = float(inst.query(':WAVeform:YINCrement?'))
    y_origin = float(inst.query(':WAVeform:YORigin?'))
    inst.query('*OPC?')
    values = np.fromstring(inst.query('WAV:DATA?'), dtype=float, sep=',')
    time_vals = x_origin + np.arange(0, values.size, dtype=float) * x_increment
    # voltage_vals = y_origin + values * y_increment
    # voltage_vals = values * y_increment
    return time_vals, values