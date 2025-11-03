#include <LiquidCrystal.h>
#include <Servo.h>
#include <string.h>
#include <stdlib.h>

// Together make the color sensor
const int LDR = A2;

const int rled = 9;
const int gled = 10;
const int bled = 11;
const int irPin = A1;
const int emPin = 7;

int rMax = 255;
int gMax = 255;
int bMax = 255;

LiquidCrystal lcd(2, 3, 4, 8, 12, 13);

int baseServoPin = 6;
const int baseMin = 148;
int baseAngle = baseMin;
const int baseMax = 40;
Servo base;
int direction = 1;
bool sweep = true;

int armServoPin = 5;
const int armRange = 70;
int armAngle = armRange;
Servo arm;
bool toPick = true;

int color       =  0;
int state       =  0;
int startColor  = -1;
int endColor    = -1;

bool endPrompt = false;
bool startPrompt = false;
bool centred = false;

void setup() {
  Serial.begin(9600);
  
  pinMode(LDR, INPUT);
  pinMode(rled,OUTPUT);
  pinMode(gled,OUTPUT);
  pinMode(bled,OUTPUT);

  pinMode(irPin, INPUT);
  pinMode(emPin, OUTPUT);
  
  lcd.begin(16, 2);
  lcd.setCursor(0,1);
  
  base.attach(baseServoPin);
  arm.attach(armServoPin);
  
  arm.write(armRange);
  base.write(baseAngle);
  lcd.write("start");
  delay(1000);
  lcd.clear();
}


void loop() {
 
  // State 0 = INPUT PICK AND DROP LOCATIONS
  if (state == 0) {
    if (startColor == -1){
      if(startPrompt == false){
          Serial.println(" Hello! ");
          Serial.println("Enter start colour: 1-red, 2- green, 3- blue");
          lcd.print("Enter: 1-red");
          lcd.setCursor(0,1);
          lcd.print("2-green,3-blue");
          startPrompt = true;
          delay(4000);

          
      }
    if (Serial.available() ==0){
          startPrompt = false;
    }
    if (Serial.available() > 0 && startPrompt == true) {
      
        startColor = Serial.parseInt();
        if (startColor == 1){
      Serial.println(" Start:red ");
        }
        if (startColor == 2){
      Serial.println(" Start: green ");
        }
        if (startColor == 3){
      Serial.println(" Start: blue ");
        }
        lcd.clear();
        lcd.print("Start: " + String(startColor));
    }
    }
    
    if (endColor == -1){
      if(endPrompt == false){
          Serial.println("Enter end colour: ");
          lcd.clear();
          lcd.print("End colour: ");
          endPrompt = true;
          delay(4000);
      }
       if (Serial.available() == 0){
          endPrompt = false;
    }
      if (Serial.available()>0 && endPrompt == true){

        endColor = Serial.parseInt();
        if (endColor == 1){
      Serial.println(" End :red ");
        }
        if (endColor == 2){
      Serial.println(" End: green ");
        }
        if (endColor == 3){
      Serial.println(" End: blue ");
        }
        lcd.clear();
        lcd.print("End: " + String(endColor));

      delay(1000);
      state = 1;
      }
    }
    

    }
  

  // State 1 = PERFORM ACTION

  if (state == 1) {
    color = stripColor();

    if (color == startColor && toPick == true) {
      
      if (centred == false){
      if (direction == 1){
        baseAngle -=  3;
        base.write(baseAngle);}
      else if (direction == 0){
        baseAngle += 15;
        base.write(baseAngle);
      }
      centred = true;
      delay(500);
      }
      
      // Object detection and arm retrieve
      // if (analogRead(irPin) < 23) {
      //   Serial.println("Picked Object");
      //   digitalWrite(emPin, HIGH);
      //   delay(3000);
      //   arm.write(armRange);
      //   armAngle = armRange;
      //   sweep = true;
      //   toPick = false;
      // }
      // else { // Arm descends to pick the object
      //   Serial.println("Descending" + String(armAngle));
      //   armAngle -= 2;
      //   arm.write(armAngle);
      //   sweep = false;
      // }
      if (armAngle > 0) {  
        Serial.println("Descending " + String(armAngle));
        armAngle -= 2;
        arm.write(armAngle);
        sweep = false;
    }
    else {  
        Serial.println("Picked Object");
        digitalWrite(emPin, HIGH);
        delay(3000);
        armAngle = armRange;  
        arm.write(armAngle);
        // if (armAngle < armRange) {
        //     armAngle += 2;
        //     arm.write(armAngle);
        // }
        
        sweep = true;
        toPick = false;
        centred = false;  
    }
    }
    if (color == endColor && toPick == false) {
        
      if (centred == false){
      if (direction == 1){
        baseAngle -= 3 ;
        base.write(baseAngle);}
      else if (direction == 0){
        baseAngle += 15;
        base.write(baseAngle);
      }
      centred = true;
      delay(500);
      }
      
      // Object dropped and arm retrieves
      // if (analogRead(irPin) < 15) {
      //   // Switch OFF emPin
      //   Serial.println("Dropped object");
      //   digitalWrite(emPin, LOW);
      //   arm.write(armRange);
      //   sweep = true;
      //   state = 0;
      //   toPick = true;
      //   armAngle = armRange;
        
      //   startColor = -1;
      //   endColor = -1;

      //   endPrompt = false;
      //   startPrompt = false;
      // }
      // else { // arm descends to drop the object
      //   armAngle -= 2;
      //   arm.write(armAngle);
      //   sweep = false;
      // }

      if (armAngle > 0) {  
        Serial.println("Descending " + String(armAngle));
        armAngle -= 2;
        arm.write(armAngle);
        sweep = false;
    }
    else {  
        Serial.println("Dropped Object");
        digitalWrite(emPin, LOW);
        delay(1000);
        armAngle =armRange;  
        arm.write(armAngle);  
        
        // if (armAngle < armRange) {
        //     armAngle += 2;
        //     arm.write(armAngle);
        // }
        
        sweep = true;
        toPick = true;
        centred = false;  
        state = 0;
        startColor = -1;
        endColor = -1;
        endPrompt = false;
        startPrompt = false;
    }

    }

    if (sweep == true) {
        if (baseAngle <= baseMax) direction = 0;
    if (baseAngle >= baseMin) direction = 1;
      if (direction == 0) {
        baseAngle += 3;
     }
     else if (direction == 1) {
        baseAngle -= 3;
     }

    base.write(baseAngle);

    }

  }

  if (state == 2) {
    int data = 0;
    data = analogRead(irPin);
    lcd.setCursor(0, 1);
    lcd.print(data);
    Serial.println(data);
  }
}


int stripColor() {
  int rVal = 0;
  int gVal = 0;
  int bVal = 0;

  // RED
  setColor(rMax, 0, 0);
  delay(50);
  rVal = analogRead(LDR);
  delay(100);

  // GREEN
  setColor(0, gMax, 0);
  delay(50);
  gVal = analogRead(LDR);
  delay(100);

  // BLUE
  setColor(0, 0, bMax);
  delay(50);
  bVal = analogRead(LDR);
  delay(100);

  if (rVal < gVal && rVal < bVal) {
    lcd.clear();
    lcd.print("Red");
    return 1;
  }
  
  if (gVal < bVal && gVal < rVal) {
    lcd.clear();
    lcd.print("Green");
    return 2;
  }
  
  if (bVal < rVal && bVal < gVal) {
    lcd.clear();
    lcd.print("Blue");
    return 3;
  }
}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(rled, redValue);
  analogWrite(gled,  greenValue);
  analogWrite(bled, blueValue);
}    