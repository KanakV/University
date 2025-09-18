#include <LiquidCrystal.h>

const int LDR = A3;
LiquidCrystal lcd(2, 3, 4, 8, 12, 13);
int ldrValue = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LDR, INPUT);
  lcd.begin(16, 2);
}

void  loop() {
  lcd.setCursor(0, 1);
  
  ldrValue = analogRead(LDR);
  Serial.print(ldrValue);
  
  lcd.print(ldrValue);
  delay(500);
}

    