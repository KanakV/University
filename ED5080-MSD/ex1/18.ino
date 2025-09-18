#include <LiquidCrystal.h>
#include <string.h>

unsigned long startTime;
unsigned long currTime;

LiquidCrystal lcd(2, 3, 4, 8, 12, 13);

int const ldrPin = A3;

int ldrStatus = 0;
int ldrCount = 0;

void setup() {
  Serial.begin(9600);
  pinMode(ldrPin, INPUT);
  lcd.begin(16, 2);
}

void  loop() {
  lcd.setCursor(0, 0);

  lcd.print("Starting in 1");
  lcd.setCursor(0, 1);
  lcd.print("second");
  delay(1000);

  startTime = millis();
  currTime = millis();
  int timeElapsed = currTime - startTime;

  lcd.clear();
  while(timeElapsed <= 5000) {
    ldrStatus = analogRead(ldrPin);

    // CHECK IF HAND IS PRESENT
    if (ldrStatus > 800) {
      ldrCount += 1;
    }

    // DIPLAY TIME REMAINING
    int timeLeft = 5000 - timeElapsed;
    int sec = int(timeLeft / 1000);
    int milsec = timeLeft % 1000;

    char strTime[7];
    sprintf(strTime, "%d:%d", sec, milsec);
    lcd.setCursor(0, 0);
    lcd.print(strTime);


    // UPDATE CURRENT TIME
    currTime = millis();
    timeElapsed = currTime - startTime;
  };
  lcd.clear();

  lcd.print(ldrCount);
  delay(5000);
  lcd.clear();
}

