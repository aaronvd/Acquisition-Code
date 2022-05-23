import os
import csv
import sys
import random
from urllib import request

# Note: please go to the bottom of the program to initiate funciton calls

def GenerateRandomTS(n):
  for i in range(1,n+1):
      filename = "TuningStates"+str(i)+".csv"
      with open(filename, 'w', newline='') as csvfile:
          fd = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
          for _ in range(1024):
              fd.writerow([random.randint(0, 255) for _ in range(240)])

def ArduinoGenerate(filenames):
  #Generate 16 worker Arduino .ino files
  comment = """\n//MEGA: (LATCH:10), (DATA:51), (CLOCK:52)
              //UNO: (LATCH: 9), (DATA: 11), (CLOCK: 13)"""
  head1 = "#include <SPI.h> \n#include <Wire.h> \n#define M0 0 \n#define W0 1\n#define NWorker " + str(len(filenames))
  head2 = """\n\nconst int latchPin = 10; 
const int dataPin = 51; 
const int clockPin = 52; 
const int LED = 53;
bool success = false;

//Data matrix that stores all the tuning state the ProgramMemory = 256KB
const byte data_zero [240] PROGMEM = {0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000,0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000};
"""
  setup = """\n\nvoid setup(){
  Serial.begin(115200);
  Serial.flush();
  SPI.begin();

  pinMode(LED, OUTPUT);
  pinMode(latchPin, OUTPUT); 
  pinMode(dataPin, OUTPUT); 
  pinMode(clockPin, OUTPUT); // not needed
  digitalWrite(latchPin, HIGH); // init HIGH, LOW=write

  Wire.begin(W0);                // join i2c bus with address Wid
  Wire.onReceive(receiveEvent); // ouput voltages
  Wire.onRequest(requestEvent); // send ack back

  Serial.println();
  Serial.print("Worker "); Serial.print(Wid); Serial.println(" begun");
}"""
  requestEvent = """\n\nvoid requestEvent(){
  //Ackowledge Master that worker has done setting TuningStates
  if(success){
    Serial.println("ACK sent");
    Wire.write(Wid);  //Write back on separate channel
    Wire.begin(W0);
  }
  digitalWrite(LED, 1); delay(700);
  digitalWrite(LED, 0); delay(50);
}"""
  receiveEvent = """\n\nvoid receiveEvent(int byteRead){
  Serial.print("Command from master recieved, data=");
  success=false;
  int section = Wire.read();
  int index = Wire.read();
  
  //Decode data sent (section, index)
  Serial.print("Index recieved: "); Serial.println(section*128 + index);
  select_data_and_deliver(section, index);
  Serial.println("  Tuning states are successfully sent");

  success = true;
  Wire.begin(Wid);
  digitalWrite(LED, 1); delay(300);
  digitalWrite(LED, 0); delay(50);
}"""
  select_data_and_deliver= """\n\nvoid select_data_and_deliver(int sec, int index){
  switch (sec) {
    case 0:
      setTuningState(data1[index]);  break;
    case 1:
      setTuningState(data2[index]);  break;
    case 2:
      setTuningState(data3[index]);  break;
    case 3:
      setTuningState(data4[index]);  break;
    case 4:
      setTuningState(data5[index]);  break;
    case 5:
      setTuningState(data6[index]);  break;
    case 6:
      setTuningState(data7[index]);  break;
    case 7:
      setTuningState(data8[index]);  break;
    default:
      success = false;
  }
}"""
  setTuningState = """\n\nvoid setTuningState(byte states[240]){
  digitalWrite(latchPin, HIGH);
  for(int j = 0; j < 8; j++){
    digitalWrite(latchPin, LOW); 
    for(int i = 0; i < 30; i++){
      unsigned int instruction = convertToLong(states[j+i*8], j+1);
      SPI.transfer16(instruction);
    }
    digitalWrite(latchPin, HIGH);
  }
  
}"""
  convertToLong = """\n\nunsigned int convertToLong(byte val_255, int index){
  //if there are issues w/ index int, change to byte on all inst.
  unsigned int instruction = 0;
  instruction += (val_255 << 4);
  instruction += (index << 12);
  return instruction;
}"""
  loop = "\n\n\nvoid loop(){\n  delay(100);\n}"

  for i in range(len(filenames)):
    output_filename = "worker"+str(i+1)+"/worker"+str(i+1)+".ino"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    workerID = i+2

    with open(output_filename, 'w', newline='\n') as outfile:
      outfile.write("\n//Worker No." + str(workerID) + "\n")
      outfile.write(head1)
      outfile.write("\n#define Wid " + str(workerID))
      outfile.write(comment)
      outfile.write(head2)

      #Read data from csv file and write to Arduino file
      with open(filenames[i], newline='') as csvfile:
        fd = csv.reader(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        data = "const byte data1 [128][240] PROGMEM = {\n"
        counter = 0
        data_sec = 1
        for row in fd:
          #Dividing the csv into groups of 128 tuning states, each of 240 bytes long
          if (counter == 128):
            counter = 0
            data_sec += 1
            data += "};\n"
            if (data_sec != 9):
              data += "const byte data" + str(data_sec) +" [128][240] PROGMEM = {\n"
  
          #Add a comment every 10 lines within one data block of legnth 128
          if (counter % 10 == 0):
            data += "  /*" + str(counter) + "*/\n"
          
          #Convert integer 0~255 to bytes 0b00000000~0b11111111
          data += "   {"
          for n in row[0].split(","):
            data += f'0b{int(n):08b}' + ", "
          data = data[:-2] + "},\n"
          counter += 1
        data += "};\n"
        outfile.write(data)

      outfile.write(setup)
      outfile.write(requestEvent)
      outfile.write(receiveEvent)
      outfile.write(select_data_and_deliver)
      outfile.write(setTuningState)
      outfile.write(convertToLong)
      outfile.write(loop)
  
  MakeMasterIno(len(filenames))

def MakeMasterIno(nworker):
  #Generate master Arduino .ino file
  head1 = "//Master.io\n\n#include <Wire.h>\n#include <SPI.h>\n#define M0 0\n#define W0 1\n"
  head2 = "#define NumWorkers " + str(nworker) + "\n\n#define latchPin 10\n#define dataPin  51\n#define clockPin 52\n"
  head3 = "\nbool check[" + str(nworker) + "] = {" + ("false, " * nworker)[:7*nworker-2] + "};"
  setup = """\n\nvoid setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  SPI.begin();
  Wire.begin(M0);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  
  pinMode(dataPin, OUTPUT);
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  digitalWrite(latchPin, HIGH); //init @ HIGH; LOW to write
  digitalWrite(clockPin, HIGH);
  Serial.println("Master Start");
}"""
  loop = """\n\nvoid loop(){
  //Wait to receive data from onboard computer
  while (Serial.available()){
    int index = Serial.readString().toInt();
    Serial.print("Received from computer index: "); Serial.print(index);
    broadcastToWorkers(index);

    //TODO: send back the information of this particular index
      //Same Serial Port
  }
}
"""
  broadcastRegular = """\n\nvoid broadcastToWorkers(int dataIndex){
  //Master broadcasts index to all devices
  Wire.beginTransmission(W0);
  Wire.write(dataIndex / 256);  //First byte of data = section/opcode
  Wire.write(dataIndex % 256);  //Second byte of data = index
  Wire.endTransmission();

  do {
    Serial.println("Waiting for some worker to finish");
    delay(10);
    for(int workerID = 2; workerID < 2 + NumWorkers; workerID++) {
      Wire.requestFrom(workerID, 1);
      int id = Wire.read();
      check[id - 2] = true;
      delay(10);
  
      Serial.print(id); Serial.print(" Array:");
      printArray();
    }

  } while(!checkArray());
  
  
  //Write back to computer
  Serial.print("!Done");
}
"""  
  checkArray = """\n\n\nbool checkArray(){
  //Check if all workers have finished
  for(int i=0; i<NumWorkers; i++)
    if(!check[i]){
      return false;
  }

  //Clear the worker array
  for(int i=0; i<NumWorkers; i++)
    check[i] = false;
  return true;
}"""
  printArray = """\n\nvoid printArray(){
  for(int i=0; i<NumWorkers; i++){
    Serial.print(check[i]);
  }
  Serial.println();
}"""
  receiveEvent = """\n\n\nvoid receiveEvent(int howMany){
  Serial.println("Event recieved"); 
  int x = Wire.read();
  Serial.println(x);
}"""
  requestEvent = """\n\nvoid requestEvent(){
  Serial.println("Event Requested");
}"""

  master_filename = "master/master.ino"
  os.makedirs(os.path.dirname(master_filename), exist_ok=True)
  with open(master_filename, 'w', newline='\n') as outfile:
    outfile.write(head1)
    outfile.write(head2)
    outfile.write(head3)
    outfile.write(setup)
    outfile.write(loop)
    outfile.write(broadcastRegular)
    outfile.write(checkArray)
    outfile.write(printArray)
    outfile.write(receiveEvent)
    outfile.write(requestEvent)



            
### Control Codes ###
names = []
if len(sys.argv) == 1:
  #Default list of csv files to look for
  names = ["TuningStates1.csv", "TuningStates2.csv"] #, "TuningStates3.csv", "TuningStates4.csv", "TuningStates5.csv", "TuningStates6.csv", "TuningStates7.csv", "TuningStates8.csv", "TuningStates9.csv", "TuningStates10.csv", "TuningStates11.csv", "TuningStates12.csv", "TuningStates13.csv", "TuningStates14.csv", "TuningStates15.csv", "TuningStates16.csv"]
else:
  names = sys.argv[1:]

#Uncomment the following to run the script
# GenerateRandomTS(1)               #Generate random tuning state for 16 boards
# MakeMasterIno(len(names))        #If we only want to make the master Arduino file for len(names) workers
ArduinoGenerate(names)           #Automatically make all worker and master Arduino files
