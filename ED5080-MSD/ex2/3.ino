#include <LiquidCrystal.h>
#include <string.h>
#include <stdio.h>

LiquidCrystal lcd(2, 3, 4, 8, 12, 13);

const int prox  = 6;
const int led   = 12; 

void setup() {
  lcd.begin(16, 2);
  pinMode(prox, INPUT);
  pinMode(led, OUTPUT);
}

void loop() {
  int proxValue = digitalRead(prox);

  if (proxValue == HIGH) {
    digitalWrite(led, LOW);
  }
  else {
    digitalWrite(led, HIGH);
  };
}

