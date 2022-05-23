#AVG: 2 seconds

import serial
import time
import numpy as np

startOfData = '<'
endOfData = '>'

startOfInputLen = 's'
endOfInputLen = 'e'
sentInputLen = False

recordingData = False
readyToPrint = False
dataBuffer = ""

"""
On use of voltage_matrix_30:
Matrix is ordered as Pin 1 - 8, with each row containing values for 3 of the DACS. On the 30 DAC
board the input [5.0, 4.5, 4.2, 3.2, 1.2, 2.0, 3.3, 4.7] looks like:
[5.0 |DIVIDER| 4.5]
[4.2 |DIVIDER| 3.2]
[1.2 |DIVIDER| 2.0]
[3.3 |DIVIDER| 4.7]
"""

def initializeArduino(numDACs, comPort):

    serialPort = setSerial(115200, comPort, numDACs)
    sendInputLen(serialPort)
    msg = receiveFromArduino(serialPort)

    while msg.find("Received: " + str(numDACs) + " from serial.") == -1:
        msg = receiveFromArduino(serialPort)
        
    if not (msg == "NO VAL"):
        print(msg)

    return serialPort


def setSerial(baudRate, porT, expInputs):
    """
        setSerial sets up the connection between Python and the Arduino.
        - baudRate should remain at 115200;
        - porT is the serial port with which the computer sends and receives serial data. On MAC devices this will
          be represented as "dev/cu.usbmodemXXXXX" or "dev/tty.usbmodemXXXXX". On Windows devices it is "COMXX";
        - expInputs defines the number of DACs the Arduino should expect.
    """

    # global serialPort
    global expectedInstructions

    expectedInstructions = expInputs
    serialPort = serial.Serial()
    serialPort.baudrate = baudRate
    serialPort.port = porT
    serialPort.open()

    sendReadyCheck(serialPort)

    return serialPort

def sendReadyCheck(serialPort):
    """
        sendReadyCheck establishes an initial handshake between the Arduino and Python. Until the Arduino returns
        that it is ready to receive data, the program waits.
    """

    msg = ""
    while msg.find("READY") == -1:
        msg = receiveFromArduino(serialPort)
        if not (msg == "NO VAL"):
            print(msg)

def getInstruction(pinSpace255ValInstruction):
    """
        getInstruction converts a string in the format "PIN 255VAL PIN 255VAL PIN 255VAL ..." for n pins and values
        into a string representing the integer version of the 16 bit binary instruction.

        i.e. "1 255 1 255" is converted into "8176 8176", readable by the Arduino.

        NOTE: This function can experience errors when raw inputs with a space at the end are used. If not using one
        of the provided tester functions, be sure to remove extra end spaces.
    """
    values_in_array = pinSpace255ValInstruction.split(' ')

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

def sendToArduino(serialPort, stringData):
    """
        sendToArduino sends some stringData to the Arduino, in a readable form. The Arduino only recognizes data with
        the characters '<' and '>' at the end to be data, so this function attaches those characters and sends to the
        Arduino.
        It is encoded with utf-8 to match input type, and since there are no expected inputs out of utf-8, unicode
        error handling is not present.
    """
    # global serialPort

    processedStringData = startOfData
    processedStringData += stringData
    processedStringData += endOfData

    serialPort.write(processedStringData.encode('utf-8'))

def sendInputLen(serialPort):
    """
        sendInputLen tells Arduino the number of DAC instructions it should expect. This is differentiated from
        DAC instructions with the characters 's' and 'e'.

        NOTE: In later edits this function can be combined with sendToArduino.
    """
    # global serialPort

    processedStringData = startOfInputLen
    processedStringData += str(expectedInstructions)
    processedStringData += endOfInputLen

    serialPort.write(processedStringData.encode('utf-8'))

def receiveFromArduino(serialPort):
    """
        receiveFromArduino stores each piece of serial data received from the Arduino until we have the full message.
        This function is often run in a while loop, so that it may continually seek a startOfData or endOfData signal
        from the Arduino.

        When the startOfData signal is received, recordingData is set to True so that the program stores all incoming
        serial data to dataBuffer.

        When the endOfData signal is received, recordingData is set to False and readyToPrint is set to True. This cuts
        off any more serial data from being recorded, and returns the complete string in the dataBuffer, then clears it.
        Before the dataBuffer is ready to print, "NO VAL" is returned, which can be used as a condition for while loops.
    """
    # global serialPort, dataBuffer, recordingData, readyToPrint
    global dataBuffer, recordingData, readyToPrint

    if serialPort.inWaiting() > 0 and (not readyToPrint):
        dataIn = serialPort.read().decode('utf-8')

        if recordingData and (dataIn != endOfData):
            dataBuffer += dataIn
            #print(dataIn) for use with serial data debugging

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

def convertInstruction(arr):
    """
        convertInstruction turns any matrix of 0-5 voltage values into a matrix of 0-255 voltage values that can be
        read by the DAC.
    """

    values = []

    for x in range(len(arr)):
        temp_255_scaled = str(int((float(arr[x]) / (5.0)) * 255))
        values.append(temp_255_scaled)

    return values

def convertArrayofInstructions(array):
    """
        convertArrayofInstructions is a helper function for testProgram30DAC. Instead of using a matrix to correct the
        order of instructions as in testProgram12DAC, this does it algorithmically for the 30 DAC board. It organizes
        the instructions such that the output of the board is in the order of DAC# Pin#, left to right and up to down.
    """

    inputs = array

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


def testProgram30DAC(serialPort, voltage_matrix_30):
    """
        This function sets the voltage on the 30 DAC board using the voltage_matrix_30 above. Refer to the confluence
        documentation on its use.
    """

    arrayOfVoltages = convertInstruction(voltage_matrix_30)
    arrayofInstructions = convertArrayofInstructions(arrayOfVoltages)

    arduinoReply = ""

    while len(arrayofInstructions) >= 0:
        try:
            x = getInstruction(arrayofInstructions[len(arrayofInstructions) - 1])
        except IndexError:
            break

        sendToArduino(serialPort, x)
        lastinstruction = arrayofInstructions.pop()
        lastinstruction2 = getInstruction(lastinstruction).split(' ')[:-1]

        while arduinoReply.find("Received: " + str(lastinstruction2[len(lastinstruction2) - 1]) + " from serial!") == -1:
            arduinoReply = receiveFromArduino(serialPort)


def testProgram12DAC(serialPort, voltage_matrix_12):
    """
        This function sets the voltage on the 12 DAC board using the voltage_matrix_12 above. Refer to the confluence
        documentation on its use.

        NOTE: This function uses a matrix to correct the order rather than a function.
    """
    # arrayOfVoltages = convertInstruction(voltage_matrix_12)

    correction_matrix = [1,  49, 2,  50, 3,  51, 4,  52, 5,  53, 6,  54,
                         13, 61, 14, 62, 15, 63, 16, 64, 17, 65, 18, 66,
                         25, 73, 26, 74, 27, 75, 28, 76, 29, 77, 30, 78,
                         37, 85, 38, 86, 39, 87, 40, 88, 41, 89, 42, 90,
                         60, 12, 59, 11, 58, 10, 57,  9, 56,  8, 55,  7,
                         72, 24, 71, 23, 70, 22, 69, 21, 68, 20, 67, 19,
                         84, 36, 83, 35, 82, 34, 81, 33, 80, 32, 79, 31,
                         96, 48, 95, 47, 94, 46, 93, 45, 92, 44, 91, 43]

    # dictionary = dict(zip(correction_matrix, arrayOfVoltages))
    dictionary = dict(zip(correction_matrix, voltage_matrix_12))
    instruction = ""
    arrayOfInstructions = []

    for key in sorted(dictionary):
        instruction = str(int((key + 11) / 12)) + " " + str(dictionary[key]) + " " + instruction #if reversed fix here
        if key % 12 == 0:
            arrayOfInstructions.append(instruction[:-1])
            instruction = ""

    arduinoReply = ""

    while len(arrayOfInstructions) >= 0:
        try:
            x = getInstruction(arrayOfInstructions[len(arrayOfInstructions) - 1])
        except IndexError:
            break

        sendToArduino(serialPort, x)
        lastinstruction = arrayOfInstructions.pop()
        lastinstruction2 = getInstruction(lastinstruction).split(' ')[:-1]

        while arduinoReply.find("Received: " + str(lastinstruction2[len(lastinstruction2) - 1]) + " from serial!") == -1:
            arduinoReply = receiveFromArduino(serialPort)

