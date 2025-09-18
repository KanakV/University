#include <LiquidCrystal.h>
#include <string.h>
#include <stdio.h>

LiquidCrystal lcd(2, 3, 4, 8, 12, 13);

String msg;

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
}

void  loop() {
  
  int num1, num2;
  char buffer[4];
  msg = Serial.readString();
  msg.trim();
  
  strncpy(buffer, msg.c_str() + 1, 3);
  buffer[3] = '\0'; 
  num1 = atoi(buffer);

  strncpy(buffer, msg.c_str() + 5, 3);
  buffer[3] = '\0'; 
  num2 = atoi(buffer);

  Serial.print(num2);

  lcd.setCursor(0, 0);
  lcd.print("Num1: ");
  lcd.print(num1);

  lcd.setCursor(0, 1);
  lcd.print("Num2: ");
  lcd.print(num2);
}

