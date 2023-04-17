import serial
import time
import numpy as np

from VNA_control import *

def create_instruction(tuning_state: np.ndarray, output_type='DAC', eof=str(999999999)):
    '''Creates instruction strings to be sent by Arduino. Tuning state is given as 1D array of values in order of pins.'''
    if output_type == 'DAC':
        tuning_state = np.flip(tuning_state.reshape((-1, 8)).T, axis=1)

        instructions = []  # instruction array size 8 containing strings.
        r = 0
        for row in tuning_state:
            r += 1
            instruction_str = ""
            for entry in row:
                instruction_str += (str(((r << 12) | (15) | (entry << 4))) + " ")

            instructions.append(instruction_str + eof)

    elif output_type == 'shift_register':
        tuning_state = np.reshape(np.flip(tuning_state), (-1, 8))
        instructions = ""
        
        for i in range(tuning_state.shape[0]):
            instruction_str = ""
            for j in range(8):
                instruction_str += str(tuning_state[i,j])
            instructions += str(int(instruction_str, 2)) + " "

        instructions = [instructions + eof]

    return instructions

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
        out = VNA_initiate(self.device, self.parameters['nf'],
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
        m = VNA_read(self.device, s)
        return m

class Arduino:
    def __init__(self, baudrate: int, port: str, eof: any = 999999999):
        self.device = {}
        self.port = port
        self.baudrate = baudrate
        self.eof = str(eof)

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

    def write_handshake(self, data_out: str, handshake=True):
        start_time = time.time()
        self.device.write(bytes(data_out, 'utf-8'))

        if handshake:
            # Wait until Done signal received from Arduino
            done = 0
            while done == 0:
                data_in = self.device.readline()
                if data_in == bytes("Done\r\n", 'utf-8'):
                    done = 1
                    print("Data received by Arduino (Time Elapsed: %s)" %
                        (time.time() - start_time))
                else:
                    time.sleep(0.001)

    def apply_tuning_state(self, instructions, handshake=True):
        for instr in instructions:
            self.write_handshake(instr, handshake)

    # Closes serial port; prevents error after program termination when used
    def close(self):
        self.device.close()