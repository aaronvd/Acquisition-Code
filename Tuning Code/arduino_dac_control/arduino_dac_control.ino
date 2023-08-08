#include <SPI.h>

long index;
int len = 14;   // # of DACs
int temp = 0;

// Pin config. for Uno
//const int dataPin = 11;
//const int clockPin = 13;
//const int latchPin = 9;

// Pin config. for Mega
const int dataPin = 51;
//const int clockPin = 52;
const int latchPin = 49;

void setup() {
  SPI.begin();
  Serial.begin(115200);
  Serial.flush();

  pinMode(dataPin, OUTPUT); 
  //pinMode(clockPin, OUTPUT);
  pinMode(latchPin, OUTPUT); 

  digitalWrite(latchPin, HIGH);

  Serial.println("Ready");
}

void loop() {
  while (!Serial.available());
  digitalWrite(latchPin, LOW);
  temp = 0;
  
  while (Serial.available()){
    index = Serial.parseInt();
    SPI.transfer16(index);
    temp = temp + 1;

    if (temp == len){
      digitalWrite(latchPin, HIGH);
      Serial.flush();
      break;
    }
  }
}

