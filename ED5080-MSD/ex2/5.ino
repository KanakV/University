#include <Servo.h>

Servo servo;
int angle = 90;
bool sweep = false;
bool direction = true;

void setup() {
  servo.attach(6);
  Serial.begin(9600);
  servo.write(angle);
}

void loop() {
  if (Serial.available() > 0) {
    char val = Serial.read();

    if (val == '1') {
      sweep = true;   
    }
    if (val == '2') {
      sweep = false;  
    }
  }

  if (sweep == true) {  
    if (direction && angle < 180) {
      angle++;
    } else if (!direction && angle > 0) {
      angle--;
    }

    if (angle >= 180) direction = false;
    if (angle <= 0) direction = true;

    servo.write(angle);
    delay(30);
  }
}
