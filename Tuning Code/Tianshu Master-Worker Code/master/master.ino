//Master.io

#include <Wire.h>
#include <SPI.h>
#define M0 0
#define W0 1
#define NumWorkers 2

#define latchPin 10
#define dataPin  51
#define clockPin 52

bool check[2] = {false, false};

void setup() {
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
}

void loop(){
  //Wait to receive data from onboard computer
  while (Serial.available()){
    int index = Serial.readString().toInt();
    Serial.print("Received from computer index: "); Serial.print(index);
    broadcastToWorkers(index);

    //TODO: send back the information of this particular index
      //Same Serial Port
  }
}


void broadcastToWorkers(int dataIndex){
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



bool checkArray(){
  //Check if all workers have finished
  for(int i=0; i<NumWorkers; i++)
    if(!check[i]){
      return false;
  }

  //Clear the worker array
  for(int i=0; i<NumWorkers; i++)
    check[i] = false;
  return true;
}

void printArray(){
  for(int i=0; i<NumWorkers; i++){
    Serial.print(check[i]);
  }
  Serial.println();
}


void receiveEvent(int howMany){
  Serial.println("Event recieved"); 
  int x = Wire.read();
  Serial.println(x);
}

void requestEvent(){
  Serial.println("Event Requested");
}