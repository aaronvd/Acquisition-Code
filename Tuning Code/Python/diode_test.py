#%%
import serial
import time
import numpy as np

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
    def __init__(self, arduino: Arduino, eof: any = 999999999):
        self.arduino = arduino
        self.eof = str(eof)

        self.arduino.initialize_device()

    def _create_instruction(self, ordered_tuning_state: np.ndarray):
        ordered_tuning_state = np.reshape(ordered_tuning_state, (-1, 8))
        instruction = ""  # instruction array size 8 containing strings.
        
        for i in range(ordered_tuning_state.shape[0]):
            instruction_str = ""
            for j in range(8):
                instruction_str += str(ordered_tuning_state[i,j])
            instruction += str(int(instruction_str, 2)) + " "

        instruction = instruction + self.eof

        return instruction

    def apply_tuning_state(self, tuning_state: np.ndarray):
        # Order tuning state here: tuning_state = order(tuning_state)
        self.instruction = self._create_instruction(tuning_state)

        self.arduino.write_handshake(self.instruction)
        # Can add measurement line here if need to collect measurements

    def close_arduino(self):
        self.arduino.close()


#%%
# Example
# ordered_tuning_state = np.array([[0, 255, 0, 255, 0, 255, 0, 255],
#                                  [255, 255, 255, 255, 255, 255, 255, 255]]).T
# Note: This array sets each 1st DAC element to 255, then each second to 120, then each third to 0, and so on
# until the eighth DAC element. Keep in mind if DACs are daisy-chained. You might need a separate matrix/function
# to order elements to the plane of an antenna

ordered_tuning_state = np.flip(np.array([1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0]))

arduino = Arduino(baudrate=115200, port="COM4")
experiment = Experiment(arduino)
experiment.apply_tuning_state(ordered_tuning_state)
experiment.close_arduino()
