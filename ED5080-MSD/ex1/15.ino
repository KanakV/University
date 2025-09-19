#include <Servo.h>

#define max_angle 180
#define min_angle 0
const int potPin = A2;
const int servo_pin=5;


Servo servo;

void setup() {
servo.attach(servo_pin);

}

void loop() {
  int val =0;
  val = analogRead(potPin);
  val = map(val,0,1023,min_angle,max_angle);
  servo.write(val);
  delay(1000);

//SG90 max angle = 130
//MG996R max angle = 180
}
