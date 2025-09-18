const int redPin = 3;
const int greenPin = 5;
const int  bluePin = 6;

bool run = true;

void setup() {
  pinMode(redPin,  OUTPUT);              
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void  loop() {
  while (run) {
    setColor(255, 255, 255); // White 
    delay(1000);
    setColor(170, 0, 255); // Purple
    delay(1000);
    setColor(127, 127,  127); // Light Blue
    delay(1000);
    run = false;
  }
}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(redPin, redValue);
  analogWrite(greenPin,  greenValue);
  analogWrite(bluePin, blueValue);
}
