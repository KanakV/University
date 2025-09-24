#include <Servo.h>

const int ir_sensor = 6;


Servo servo;
int angle = 0;
bool sweep = false;
bool direction = true;
int val = 0;
void setup() {
  servo.attach(5);
  // servo.write(angle);
  Serial.begin(9600);
  pinMode(ir_sensor,INPUT);
}

void loop() {
  int val = digitalRead(ir_sensor);
  // Serial.print(val);

  if (val == 1) {
      sweep = true;
      Serial.print("object detected");
  }
  if (val == 0) {
      sweep = false;  
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
