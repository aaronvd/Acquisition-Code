import serial
import pyvisa as visa
import time
import numpy as np

import VNA_control as vc

def instrument_open(address):
    rm = visa.ResourceManager()
    instr = rm.open_resource(address)
    time.sleep(5)
    instr.read_termination = '\n'
    instr.write_termination = '\n'
    print(instr.query('*IDN?'))
    return instr

def create_instruction(tuning_state: np.ndarray, output_type='DAC'):
    '''Creates instruction strings to be sent by Arduino. Tuning state is given as 1D array of values in order of pins.'''
    if output_type == 'DAC':
        tuning_state = np.flip(tuning_state.reshape((-1, 8)).T, axis=1)

        instructions = []  # instruction array size 8 containing strings.
        r = 0
        for row in tuning_state:
            r += 1
            instruction_str = ""
            for entry in row:
                instruction_str += (" " + str(((r << 12) | (15) | (entry << 4))))

            instructions.append(instruction_str)

    elif output_type == 'shift_register':
        tuning_state = np.reshape(np.flip(tuning_state), (-1, 8))
        instructions = ""
        
        for i in range(tuning_state.shape[0]):
            instruction_str = ""
            for j in range(8):
                instruction_str += str(tuning_state[i,j])
            instructions += " " + str(int(instruction_str, 2))

        instructions = [instructions]

    return instructions

class Arduino:
    def __init__(self, baudrate: int, port: str):
        self.device = {}
        self.port = port
        self.baudrate = baudrate

    def initialize_device(self, timeout: int = 0.1) -> None:
        self.device = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=timeout)
        time.sleep(0.1)
        self._run_ready_check()

    def _run_ready_check(self) -> None:
        ready = 0
        while ready != 1:
            data = self.device.readline()
            if data == bytes("Ready\r\n", 'utf-8'):
                ready = 1
        print("Arduino Initialized")

    def write_handshake(self, data_out: str, handshake=True, verbose=False):
        start_time = time.time()
        self.device.write(bytes(data_out, 'utf-8'))

        if handshake:
            # Wait until Done signal received from Arduino
            done = 0
            while done == 0:
                data_in = self.device.readline()
                if data_in == bytes("Done\r\n", 'utf-8'):
                    done = 1
                    if verbose:
                        print("Data received by Arduino (Time Elapsed: %s)" %
                            (time.time() - start_time))
                else:
                    time.sleep(0.001)
        else:
            time.sleep(0.01)

    def apply_tuning_state(self, instructions, handshake=True, verbose=False):
        for instr in instructions:
            self.write_handshake(instr, handshake, verbose)

    # Closes serial port; prevents error after program termination when used
    def close(self):
        self.device.close()

class SwitchDriver:
    '''Class for initializing Agilent 11713C and controlling switch channels.'''
    def __init__(self, visa_address, N_channels=6):
        self.device = instrument_open(visa_address)
        self.N_channels = N_channels
        self.close_channels()

    def open_channels(self, channels=None, bank=1):
        if channels is None:
            channels = [i+1 for i in range(self.N_channels)]
        if isinstance(channels, int):
            channels = [channels]
        command_string = '(@'
        for channel in channels:
            command_string += str(bank)+'0'+str(channel)+','
        command_string = command_string[:-1] + ')'
        self.device.write('ROUTe:OPEn '+command_string)

    def close_channels(self, channels=None, bank=1):
        if channels is None:
            channels = [i+1 for i in range(self.N_channels)]
        if isinstance(channels, int):
            channels = [channels]
        command_string = '(@'
        for channel in channels:
            command_string += str(bank)+'0'+str(channel)+','
        command_string = command_string[:-1] + ')'
        self.device.write('ROUTe:CLOSe '+command_string)

    def close(self):
        self.device.close()

class VNA:
    '''Class for initializing VNA and reading experimental S parameter measurements.
       
       fstart, fstop (float):       start and stop frequencies for measurement IN GHZ.
                    nf (int):       # frequency points.'''
    def __init__(self, visa_address, fstart=8, fstop=12, nf=401, ifbw=1e3, power=0, calfile='', **kwargs):
        self.device = instrument_open(visa_address)
        self.parameters = {'fstart': fstart,
                           'fstop': fstop,
                           'nf': nf,
                           'ifbw': ifbw,
                           'power': power,
                           'calfile': calfile
                           }
        self.initialize_vna(**kwargs)

    def initialize_vna(self, **kwargs):
        out = vc.VNA_initiate(self.device, self.parameters['nf'],
                     self.parameters['fstart'], self.parameters['fstop'],
                     self.parameters['ifbw'], self.parameters['power'],
                     calfile=self.parameters['calfile'],
                     **kwargs)
        if kwargs.get('time_domain'):
            self.t = out
        else:
            self.f = out

    def read_vna(self, s):
        '''s (str): S parameter to read, given as string, e.g. "S11", "S21",...'''
        m = vc.VNA_read(self.device, s)
        return m