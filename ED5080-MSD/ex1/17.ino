#include <LiquidCrystal.h>

LiquidCrystal lcd(2,3,4,8,12,13);

const int lcdpin = 13;
const int sw = 9;
int count = 0;
int switch_state = 0;

void setup() {
  pinMode(lcdpin,OUTPUT);
  pinMode(sw,INPUT_PULLUP);
  lcd.begin(16,2);

}

void loop() {
  lcd.setCursor(0,1);

  while (digitalRead(sw) != NULL){
  if (digitalRead(sw)==LOW && switch_state == 0){
    switch_state = 1;
    count = count +1;
    lcd.print(count);
    delay(1000);
  }
  else
  {
    switch_state = 0;
  }
  }

}
