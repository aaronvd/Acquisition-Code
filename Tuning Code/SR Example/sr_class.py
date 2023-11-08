import serial
import time
import numpy as np

def create_instruction(tuning_state: np.ndarray):
    '''Creates instruction strings to be sent by Arduino. Tuning state is given as 1D array of values in order of pins.'''
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

    def write(self, data_out: str):
        self.device.write(bytes(data_out, 'utf-8'))
        time.sleep(0.01)

    def apply_tuning_state(self, instructions):
        for instr in instructions:
            self.write(instr)

    def close(self):
        self.device.close()
