
const int led1 = 11;
const int led2 = 12;
const int led3 = 13;


void setup() {
pinMode(led1,OUTPUT);
pinMode(led2,OUTPUT);
pinMode(led3,OUTPUT);

}

void loop() {
for (int i =0;i<0x8; i++){
 digitalWrite(led1,(i & 1)?HIGH:LOW); 
 digitalWrite(led2,(i & 2)?HIGH:LOW);
 digitalWrite(led3,(i & 4)?HIGH:LOW);
 delay(1000);

}
}
