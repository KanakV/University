#include <Servo.h>

#define max_angle 180
#define min_angle 0
const int servo_pin=5;


Servo servo;

void setup() {
servo.attach(servo_pin);

}

void loop() {
  servo.write(min_angle);
  delay(1000);

  servo.write(max_angle);
  delay(1000);

//SG90 max angle = 130
//MG996R max angle = 180
}
