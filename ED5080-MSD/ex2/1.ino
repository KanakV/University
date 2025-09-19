#include <Servo.h>

const int cw_switch = 7;
const int ccw_switch = 8;
int angle = 90;

Servo servo;

void setup() {
servo.attach(5);
pinMode(cw_switch,INPUT_PULLUP);
pinMode(ccw_switch,INPUT_PULLUP);

}

void loop() {
  int val1 = 0;
  int val2 = 0;
  
  val1= digitalRead(cw_switch);
  val2 = digitalRead(ccw_switch);

  if (val1 == 0 && angle<180){
    angle++;
    servo.write(angle);
    delay(100);
  }

  if (val2 == 0 && angle>0){
    angle--;
    servo.write(angle);
    delay(100);
  }
}

