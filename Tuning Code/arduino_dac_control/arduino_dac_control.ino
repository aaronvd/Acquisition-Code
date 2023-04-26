#include <SPI.h>

long index;
long eof = 999999999;

// Pin config. for Uno
//const int dataPin = 11;
//const int clockPin = 13;
//const int latchPin = 9;
// Pin config. for Mega
const int dataPin = 51;
const int clockPin = 52;
const int latchPin = 49;

void setup() {
  SPI.begin();
  Serial.begin(115200);
  Serial.flush();

  pinMode(dataPin, OUTPUT); 
  pinMode(clockPin, OUTPUT);
  pinMode(latchPin, OUTPUT); 

  digitalWrite(latchPin, HIGH);

  Serial.println("Ready");
}

void loop() {
  while(!Serial.available());
    index = Serial.parseInt();
    if (index == eof) {
      setState();
      //Serial.println("Done");
    }
    else {
      updateState(index);
    }
}

void setState() {
  digitalWrite(latchPin, HIGH);
  digitalWrite(latchPin, LOW);
}

void updateState(long value) {
  SPI.transfer16(value);
}
