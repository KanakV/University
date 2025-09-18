#include <LiquidCrystal.h>

LiquidCrystal lcd(2, 3, 4, 8, 12, 13);

int const ldrPin = A3;
int const ledPin = 13;

int ldrStatus = 0;


void setup() {
  Serial.begin(9600);
  pinMode(ldrPin, INPUT);
  pinMode(ledPin, OUTPUT);
  lcd.begin(16, 2);
}

void  loop() {
  lcd.setCursor(0, 0);
  ldrStatus = analogRead(ldrPin);

  if (ldrStatus > 300) {
    lcd.print(ldrStatus);
    lcd.setCursor(0, 1);
    lcd.print("LED ACTIVE");
    digitalWrite(ledPin, HIGH);
  }
  else {
    lcd.print(ldrStatus);
    lcd.setCursor(0, 1);
    lcd.print("LED INACTIVE");
    digitalWrite(ledPin, LOW);
  }

  delay(1000);
  lcd.clear();
}

