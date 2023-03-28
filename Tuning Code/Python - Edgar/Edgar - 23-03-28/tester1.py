import serial
import time
import numpy as np

from VNA_control import *

# Defines VNA to specific address set in instrument_open
class VNA:
    def __init__(self, fstart=8, fstop=12, nf=401, ifbw=1e3, power=0, calfile=''):
        self.device = instrument_open('TCPIP0::169.254.187.153::5025::SOCKET')
        self.parameters = {'fstart': fstart,
                           'fstop': fstop,
                           'nf': nf,
                           'ifbw': ifbw,
                           'power': power,
                           'calfile': calfile
                           }
        self.initialize_vna()

    def initialize_vna(self):
        print('test', '\n\n\n')
        VNA_initiate(self.device, self.parameters['nf'],
                     self.parameters['fstart'], self.parameters['fstop'],
                     self.parameters['ifbw'], self.parameters['power'],
                     calfile=self.parameters['calfile'])

    def read_vna(self, s):
        m = VNA_read(self.device, s)
        return m

# Defines Arduino given baudrate and port
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

    def write_handshake(self, data_out: str):
        start_time = time.time()
        self.device.write(bytes(data_out, 'utf-8'))

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

    # Closes serial port; prevents error after program termination when used
    def close(self):
        self.device.close()


# Defines Experiment,
class Experiment:
    def __init__(self, arduino: Arduino, vna: VNA = None, eof: any = 999999999):
        self.arduino = arduino
        self.vna = vna
        self.eof = str(eof)

        self.arduino.initialize_device()

    def _create_instruction(self, ordered_tuning_state: np.ndarray):
        assert np.size(ordered_tuning_state, 0) == 8, "Invalid/Non-ordered tuning state."

        instruction = []  # instruction array size 8 containing strings.
        r = 0
        for row in ordered_tuning_state:
            r += 1
            instruction_str = ""
            for entry in row:
                instruction_str += (str(((r << 12) | (15) | (entry << 4))) + " ")

            instruction.append(instruction_str + self.eof)

        return instruction

    def apply_tuning_state(self, tuning_state: np.ndarray):
        # Order tuning state here: tuning_state = order(tuning_state)
        instruction = self._create_instruction(tuning_state)

        for instr in instruction:
            self.arduino.write_handshake(instr)
            # Can add measurement line here if need to collect measurements

    def measure(self, s):
        return self.vna.read_vna(s)

    def close_arduino(self):
        self.arduino.close()



# Example
ordered_tuning_state = np.array([[255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
                                 [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120],
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                 [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
                                 [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120],
                                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                 [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
                                 [120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120]
                                 ])

# Note: This array sets each 1st DAC element to 255, then each second to 120, then each third to 0, and so on
# until the eighth DAC element. Keep in mind if DACs are daisy-chained. You might need a separate matrix/function
# to order elements to the plane of an antenna

arduino = Arduino(baudrate=115200, port="/dev/cu.usbmodem14101")
vna = VNA()
experiment = Experiment(arduino, vna)
experiment.apply_tuning_state(ordered_tuning_state)
experiment.close_arduino()
