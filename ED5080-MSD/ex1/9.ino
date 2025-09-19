
const int potpin = A2;
const int led = 3;

void setup() {
  pinMode(potpin,INPUT);
  pinMode(led,OUTPUT);
}

void loop() {
  int val = 0;
  val= analogRead(potpin);
  val = map(val,0,1023,0,255);
  analogWrite(led,val);
  delay(1000);
}
