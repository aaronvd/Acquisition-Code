import serial    #Use command: pip install pyserial
import time

def communicate(index):
    arduino.write(bytes(int(index), 'utf-8'))
    time.sleep(0.05)

    ready = False
    while not ready:
        if arduino.inWaiting() > 0:
            dataIn = arduino.read().decode('utf-8')
            if dataIn == "!":
                ready = True
            else:
                print(dataIn)
    ready = False
    indexInfo = arduino.readline()
    print(indexInfo)
    return


arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1)
arduino.open()

while True:
    index = input("Enter an index to select tuning state (0~1023): ")
    communicate(index)
    print("Arduino has done setting Tuning States")



#Reference:
# 1. https://create.arduino.cc/projecthub/ansh2919/serial-communication-between-python-and-arduino-e7cce0
# 2. https://pythonforundergradengineers.com/python-arduino-LED.html