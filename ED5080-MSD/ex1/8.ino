
const int pot_pin = A2;

void setup() {
  pinMode(pot_pin,INPUT);
  Serial.begin(9600);

}

void loop() {
  int val = 0;
  val = analogRead(pot_pin);
  Serial.print(val);
  delay(500);
}

