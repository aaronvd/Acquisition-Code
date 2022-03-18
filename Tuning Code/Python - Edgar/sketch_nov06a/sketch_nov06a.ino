//version w diff return prints

#include <SPI.h>

const int dataPin = 11;
const int latchPin = 9;
const int clockPin = 13;

const byte inputMaxStringSize = 255; //change this when we have longer inputs
char receivedData[inputMaxStringSize];
unsigned int receivedDataReceipt;

const byte inputLenMaxStringSize = 255;
char receivedInputData[inputLenMaxStringSize];
unsigned int receivedInputDataReceipt;
bool inputLenReceived = false;
int counter = 1;

//
boolean readyToSend = false;
boolean recordingData = false;
byte currentIndex = 0;

//
int expectedInputs;

char holderArr[16];

void setup() {
  SPI.begin();
  Serial.begin(115200);

  pinMode(dataPin, OUTPUT);
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);

  digitalWrite(latchPin, HIGH); //init @ HIGH; LOW to write
  digitalWrite(clockPin, HIGH);

  Serial.println("<READY>");

}

void loop() {  
  if(!inputLenReceived){
    inputDataToArduino();
  }
  else{
    dataToArduino();
  }
  dataToPython();
  //Serial.println("<READY>");
}

void SPIwrite(int val){
  digitalWrite(latchPin, LOW); //begin write
  SPI.transfer16(val);
  digitalWrite(latchPin, HIGH); //end write
}

void SPIwrite2(int val){
  digitalWrite(clockPin, LOW);
  SPI.transfer16(val);
  digitalWrite(clockPin, HIGH);
}

void inputDataToArduino(){
  char byteRead;
  char startOfInputLen = 's';
  char endOfInputLen = 'e';

  while(Serial.available() > 0 && !inputLenReceived){

    byteRead = Serial.read();
    
    if(recordingData && byteRead != endOfInputLen){ //if still reading dataIn & not end of dataIn
      receivedInputData[currentIndex] = byteRead;
      currentIndex += 1;
      
    }
    
    else if(recordingData && byteRead == endOfInputLen){
      receivedInputData[currentIndex] = '\0';

      //End of Data reached; Reset Vals
      recordingData = false;
      currentIndex = 0;
      readyToSend = true;

      //Convert String into an Int. //Careful w/ datatypes! //WIP here for more strings/processing
      expectedInputs = atoi(receivedInputData);

      receivedInputDataReceipt = expectedInputs;
      receivedInputData[0] = '\0'; //"Clears" array w/ zero byte
      inputLenReceived = true;
    }
    
    else if(!recordingData && byteRead == startOfInputLen){
      recordingData = true;
      
    }
  }
}

void dataToArduino(){
  char byteRead;
  char startOfData = '<'; //Note: start- and endOfData can be removed if guaranteed input size & data type
  char endOfData = '>';
  char space = ' ';

  
  while(Serial.available() > 0 && !readyToSend){
    byteRead = Serial.read();
    Serial.print(byteRead);

    if(recordingData && byteRead != endOfData){ //if still reading dataIn & not end of dataIn
      receivedData[currentIndex] = byteRead;
      currentIndex += 1;
      
    }
    
    else if(recordingData && byteRead == endOfData){
      receivedData[currentIndex] = '\0';

      //End of Data reached; Reset Vals
      recordingData = false;
      currentIndex = 0;
      readyToSend = true;

      //Convert String into an Int. //Careful w/ datatypes! //WIP here for more strings/processing

      
      
      //unsigned int valToSPI = atoi(receivedData);
      unsigned int valToSPI;
      
      //digitalWrite(latchPin, LOW);
      
      int i;
      int y;
      int z;
      char check = 'a';
      /*for(i = 0; i < (16 * expectedInputs); i++){
          holderArr[i%16] = receivedData[i];
          if(i % 16 == 15){ //not what we want
            valToSPI = atoi(holderArr);
            SPIwrite2(valToSPI); //do we need to empty array?
          }
      }*/
      digitalWrite(latchPin, LOW);
      
      y = 0;
      for(i = 0; i < expectedInputs; i++){
        z = 0;
        while(check != ' ') {
          Serial.print("here");
          check = receivedData[y+1];
          holderArr[z] = receivedData[y];
          z++;
          y++;
        }
        holderArr[z] = '\0';
        z = 0;
        Serial.print(check);
        y++;
        check = receivedData[y];
        valToSPI = atoi(holderArr);
        //Serial.print(valToSPI);
        SPIwrite2(valToSPI);
      }

      

      digitalWrite(latchPin, HIGH);
      
      //SPIwrite(valToSPI);

      
      receivedDataReceipt = valToSPI;
      receivedData[0] = '\0'; //"Clears" array w/ zero byte
    }
    
    else if(!recordingData && byteRead == startOfData){
      recordingData = true;
      
    }
      
  }
}

void dataToPython(){
  if(readyToSend && inputLenReceived && counter == 1){
    counter++;
    Serial.print("<Received: ");
    Serial.print(expectedInputs);
    Serial.print(" from serial.");
    //Serial.print(counter);
    //Serial.print(millis());
    Serial.print('>');
    
    readyToSend = false;
  }
  
  if(readyToSend){
    Serial.print("<Received: ");
    Serial.print(receivedDataReceipt);
    Serial.print(" from serial!");
    //Serial.print(millis());
    Serial.print('>');

    readyToSend = false;
  }  
}
