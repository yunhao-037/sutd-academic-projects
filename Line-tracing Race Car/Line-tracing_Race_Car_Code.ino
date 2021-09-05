#include <QTRSensors.h>

int KP = 0.01; //start by something small that just makes the bot follow the line at a slow speed
int KD = 0; //slowly increase the speeds and adjust this value. (Kp < Kd) 


#define M1_min_speed 50  //min speed of the M1
#define M2_min_speed 50  //min speed of the M2
#define M1_max_speed 150 //max speed of the M1
#define M2_max_speed 150 //max speed of the M2

#define DEBUG 0

// standard PWM DC control
int E1 = 5; // motor 1 speed control        //M1 is right wheel
int M1 = 4; // motor 1 direction control
int E2 = 6; // motor 2 speed control        
int M2 = 7; // motor 2 direction control    //M2 is left wheel

//void reverse(char a, char b) // reverse
//{
//  analogWrite(E1, a);
//  digitalWrite(M1, LOW);
//  analogWrite(E2, b);
//  digitalWrite(M2, LOW);
//}
void advance(char a, char b) // move forward
{
    analogWrite(E2, a);
    digitalWrite(M2, LOW);
    analogWrite(E1, b);
    digitalWrite(M1, HIGH);
}
//void turn_L (char a, char b) // turn left
//{
//  analogWrite(E1, a);
//  digitalWrite(M1, HIGH);
//  analogWrite(E2, b);
//  digitalWrite(M2, HIGH);
//}
//void turn_R (char a, char b) // turn right
//{
//  analogWrite(E1,a);
//  digitalWrite(M1, HIGH);
//  analogWrite(E2, b);
//  digitalWrite(M2, HIGH);
//}

int ldrPin = A0; // random pin position
int ldrStatus;

const uint8_t SensorCount = 5;
uint16_t sensorValues[SensorCount];
QTRSensorsRC qtr((unsigned char[]) {3,9,10,11,13} , SensorCount, 2500, QTR_NO_EMITTER_PIN);


//Global Variables
int limit = 900;
int motorSpeed = 0 ;
int error = 0;

void setup() {
  // put your setup code here, to run once:
  digitalWrite(LED_BUILTIN, HIGH); // turn on Arduino's LED to indicate we are in calibration mode

  for (unsigned long i = 0; i < 200; i++)
    {
        qtr.calibrate();
        Serial.println("Calibrating");
    }
    
  digitalWrite(LED_BUILTIN, LOW); // turn off Arduino's LED to indicate we are done with calibration

  // print the calibration minimum values measured when emitters were on
  Serial.begin(19200);
  delay(1000);
    
  int i;
  for (i = 4; i <= 7; i++){
    pinMode(i, OUTPUT);
  
  pinMode(ldrPin, INPUT);
  Serial.println("STARTING TO DRIVE");
}}

int lastError = 0;
void pid_calculations(){
    uint16_t sensors[5];
    uint16_t position = qtr.readLine(sensors);
    for(uint8_t i=0; i<SensorCount;i++){
    Serial.println(i,sensorValues[i]);
    Serial.println("\t");
    
    error = position - 2000; 
    motorSpeed = KP * error + KD * (error - lastError);
    lastError = error;
    Serial.println("error:");
    Serial.println(error);
    }
}

void driving(){
  int leftMotorSpeed = 80 - motorSpeed;
  int rightMotorSpeed = 80 + motorSpeed;

  if (leftMotorSpeed < 30) leftMotorSpeed = 30;
  else if (leftMotorSpeed > 255) leftMotorSpeed = M1_max_speed;
  if (rightMotorSpeed < 30) rightMotorSpeed = 30;
  else if (rightMotorSpeed > 255) rightMotorSpeed = M2_max_speed;
  Serial.println(error);
  
  if(error >= 2000){
    advance(0,70);
  }
  else if(error > 1000){
    advance(0,75);
  }
  else if(error > 0){
    advance(0,85);
  }
  else if(error == 0){
    advance(100,100);
  }
  else if(error > -1000){
    advance(85,0);
  }
  else if (error> -2000){
    advance(75,0);
  }
  else if(error <= -2000){
    advance(70,0);
  }
  

  
}

void loop() {
  // main code here, to run repeatedly:
  //start calculations and drive
  ldrStatus = analogRead(ldrPin);
  
  if(ldrStatus < limit){
    analogWrite(E1,0);
    digitalWrite(M1, HIGH);
    analogWrite(E2, 0);
    digitalWrite(M2, HIGH);
    Serial.println("ldrStatus:");
    Serial.println(ldrStatus);
    
  }
  else{
    limit = 0;
    pid_calculations();
    driving();

    Serial.println("ldrStatusNEW:");
    Serial.println(ldrStatus);

  }
}
