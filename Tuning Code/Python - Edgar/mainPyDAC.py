import serial
import time

startOfData = '<'
endOfData = '>'

startOfInputLen = 's'
endOfInputLen = 'e'
sentInputLen = False

recordingData = False
readyToPrint = False
dataBuffer = ""

#
# Voltage Matrix
# Note on Use: Matrix is ordered as Pin 1 - 8, with each row containing values for 3 of the DACS. On the 30 DAC
# board the input [5.0, 4.5, 4.2, 3.2, 1.2, 2.0, 3.3, 4.7] looks like:
# [5.0 |DIVIDER| 4.5]
# [4.2 |DIVIDER| 3.2]
# [1.2 |DIVIDER| 2.0]
# [3.3 |DIVIDER| 4.7]
#
voltage_matrix = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 0-3
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 4-6
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 7-9
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 10-12
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 13-15
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 16-18
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 19-21
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 21-24
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,       # 25-28
                  5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]     # 28-30

def getInstruction(bigString):
    values_in_array = bigString.split(' ')

    big_instruction = ""
    z = 0
    z2 = 0
    for x in range(int(len(values_in_array) / 2)):

        val255 = int(values_in_array[z]) * (2 ** 12)
        pin = int(values_in_array[z + 1]) * (2 ** 4)

        instruction = val255 | pin
        big_instruction += (str(instruction) + " ")
        z += 2
        z2 += 1

    return big_instruction

def setSerial(baudRate, porT, expInputs):
    global serialPort
    global expectedInstructions

    expectedInstructions = expInputs
    serialPort = serial.Serial()
    serialPort.baudrate = baudRate
    serialPort.port = porT
    serialPort.open()


    sendReadyCheck()

def sendToArduino(stringData):
    global serialPort

    processedStringData = startOfData
    processedStringData += stringData
    processedStringData += endOfData

    serialPort.write(processedStringData.encode('utf-8'))

def sendInputLen():
    global serialPort

    processedStringData2 = startOfInputLen
    processedStringData2 += str(expectedInstructions)
    processedStringData2 += endOfInputLen

    print(processedStringData2)

    serialPort.write(processedStringData2.encode('utf-8'))

def receiveFromArduino():
    global serialPort, dataBuffer, recordingData, readyToPrint

    if serialPort.inWaiting() > 0 and (not readyToPrint):
        dataIn = serialPort.read().decode('utf-8')

        if recordingData and (dataIn != endOfData):
            dataBuffer += dataIn

        elif recordingData and (dataIn == endOfData):
            recordingData = False
            readyToPrint = True

        elif not recordingData and (dataIn == startOfData):
            dataBuffer = ""
            recordingData = True

    if readyToPrint:

        readyToPrint = False
        return dataBuffer

    else:

        return "NO VAL"

def sendReadyCheck():
    msg = ""
    while msg.find("READY") == -1:
        msg = receiveFromArduino()
        if not (msg == "NO VAL"):
            print(msg)

def convertInstruction(arr):
    values = []

    #Get array of voltage strings
    for x in range(len(arr)):
        #temp = input("Voltage Value #" + str(x) + ": ")
        #ADD TRY HERE IF WE ARE UNCERTAIN OF VALUES
        temp_255_scaled = str(int((float(arr[x]) / (5.0)) * 255))
        #print(temp_255_scaled)
        values.append(temp_255_scaled)

    return values

def convertArrayofInstructions(array): #note: might need to reverse here!!!!!!
    inputs = array

    #print(inputs)

    counter = 0
    instruction = ""
    arrOfInstructions = []

    while counter < 8:
        for i in range(len(inputs)):
            if i % 8 == counter:
                instruction = (str((i % 8) + 1) + " " + str(inputs[i]) + " ") + instruction #fixes order, w/o is rever.
        arrOfInstructions.append(instruction[:-1])
        #print(instruction[:-1])
        instruction = ""
        counter += 1

    return arrOfInstructions

def bigBoyFunction():
    arrInst = convertArrayofInstructions()
    for b in range(len(arrInst)):
        #    print(arrInst[b])
        print(getInstruction(arrInst[b]))

def testProgram30DAC():
    """
        This tester sets the voltage on the 30 DAC board to climb from 0 to 239 on each terminal (1 to 240).
        ORDER: (1) LEFT->RIGHT, (2)TOP->DOWN.
    """

    #arrayOfVoltages = []

    #for i in range(240):
    #    arrayOfVoltages.append(i)

    arrayOfVoltages = convertInstruction(voltage_matrix)

    arrayofInstructions = convertArrayofInstructions(arrayOfVoltages)

    setSerial(115200, "/dev/cu.usbmodem14101", 30)       # Initialize connection w/ Arduino; Arduino must send <READY>
                                                        # for the program to continue. If it stops here, check Arduino
                                                        # connection.

    sendInputLen()                                      # Send Arduino the number of inputs it should expect
    msg2 = receiveFromArduino()                         # Check if Arduino received message...

    while msg2.find("Received: " + str(expectedInstructions) + " from serial. Counter: 2") == -1:
        msg2 = receiveFromArduino()
    if not (msg2 == "NO VAL"):
        print(msg2)

    prevTime = time.time()

    while len(arrayofInstructions) >= 0:
        arduinoReply = receiveFromArduino()
        if not (arduinoReply == "NO VAL"):
            print(arduinoReply + "\n")

        if (time.time() - prevTime) > 1.0:
            try:
                x = getInstruction(arrayofInstructions[len(arrayofInstructions) - 1])
            except IndexError:
                print("Program End")
                exit()

            print(x)
            sendToArduino(x)
            arrayofInstructions.pop()
            prevTime = time.time()

def testProgram2DAC():
    return 0

def testProgram1DAC():
    """
        This tester sets the voltage on the 1 DAC board to climb from 0 to 245 on each terminal (1 to 8).
        ORDER: (1) LEFT->RIGHT, (2)TOP->DOWN.
    """
    arrayOfVoltages = []
    for i in range(8):
        arrayOfVoltages.append(255)
    arrayofInstructions = convertArrayofInstructions(arrayOfVoltages)
    print(arrayofInstructions)

    setSerial(115200, "/dev/cu.usbmodem14101", 1)       # Initialize connection w/ Arduino; Arduino must send <READY>
                                                        # for the program to continue. If it stops here, check Arduino
                                                        # connection.

    sendInputLen()                                      # Send Arduino the number of inputs it should expect
    msg2 = receiveFromArduino()                         # Check if Arduino received message...

    while msg2.find("Received: " + str(expectedInstructions) + " from serial. Counter: 2") == -1:
        msg2 = receiveFromArduino()
    if not (msg2 == "NO VAL"):
        print(msg2)

    prevTime = time.time()

    while len(arrayofInstructions) >= 0:
        arduinoReply = receiveFromArduino()
        if not (arduinoReply == "NO VAL"):
            print(arduinoReply + "\n")

        if len(arrayofInstructions) == 0: #Doesnt quite work
            break

        if (time.time() - prevTime) > 1.0 and len(arrayofInstructions) > 0:
            x = getInstruction(arrayofInstructions[len(arrayofInstructions) - 1])
            print(x)
            sendToArduino(x)
            arrayofInstructions.pop()
            prevTime = time.time()

def main():
    testProgram30DAC()

main()
exit()

"""

setSerial(115200, "/dev/cu.usbmodem14301", 1)       # Initialize connection w/ Arduino; Arduino must send <READY>
                                                    # for the program to continue. If it stops here, check Arduino
                                                    # connection.

sendInputLen()                                      # Send Arduino the number of inputs it should expect
msg2 = receiveFromArduino()                         # Check if Arduino received message...

while msg2.find("Received: " + str(expectedInstructions) + " from serial. Counter: 2") == -1:
    msg2 = receiveFromArduino()
    if not (msg2 == "NO VAL"):
        print(msg2)





prevTime = time.time()
while True:
    #time.sleep(2)
    arduinoReply = receiveFromArduino()
    if not (arduinoReply == "NO VAL"):
        print(arduinoReply + "\n")

    if (time.time() - prevTime) > 1.0:
        usr_input = input("Pin-Space-Value-Space-Pin-Space-Value: ")
        print(usr_input)
        sendToArduino(getInstruction(usr_input))

        prevTime = time.time()

"""