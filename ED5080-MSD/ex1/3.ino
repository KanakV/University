
const int buttonPin = 7;
const int ledOut = 13;

int buttonState = 0;
void setup() {
  pinMode(ledOut, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  buttonState = digitalRead(buttonPin);

  if (buttonState == HIGH) {
    digitalWrite(ledOut, LOW);
  }
  else {
    digitalWrite(ledOut, HIGH);
  }  
}
