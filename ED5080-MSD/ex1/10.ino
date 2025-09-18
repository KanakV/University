#include <LiquidCrystal.h>

LiquidCrystal lcd(2, 3, 4, 8, 12, 13);

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
}

void  loop() {
  lcd.setCursor(0, 1);
  lcd.print("Hello, World");
  delay(1000);
}