#include <LiquidCrystal.h>
#include <string.h>
#include <stdio.h>

LiquidCrystal lcd(2, 3, 4, 8, 12, 13);

const int prox  = 6;

void setup() {
  lcd.begin(16, 2);
  pinMode(prox, INPUT);
  Serial.begin(9600);
}

void loop() {
  
  int proxValue = digitalRead(prox);

  lcd.setCursor(0, 0);
  lcd.print(proxValue);
  Serial.print(proxValue);
}

