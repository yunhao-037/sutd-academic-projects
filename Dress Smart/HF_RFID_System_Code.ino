#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN 10
#define RST_PIN 9
const int LED1 = 6;
MFRC522 mfrc522(SS_PIN, RST_PIN);
void setup() 
{
  Serial.begin(9600);   // Initiate a serial communication
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522
  pinMode(LED1, OUTPUT);
  digitalWrite(LED1,LOW);
  Serial.println("Bring your clothing close to the reader...");
  Serial.println();
}
void loop() 
{
  // Look for new clothes
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Select one of the clothes
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  //Show UID on serial monitor
  Serial.print("UID tag :");
  String content= "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     Serial.print(mfrc522.uid.uidByte[i], HEX);
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  Serial.println();
  Serial.print("Message : ");
  content.toUpperCase();
  if (content.substring(1) == "99 62 75 A2") 
  //change here the UID of the tag/tags that you want to give access to.
  {
    Serial.println("Let's wear this today!");
    Serial.println();
    digitalWrite(LED1, HIGH);
  }
  else 
  //if (content.substring(1) == "60 C9 CC B6" or "3A 78 F8 DD") 
  {
    Serial.println("Wrong piece of clothes taken. Please take the right one"); 
    Serial.println();
    digitalWrite(LED1, LOW);
  }
}
