// Include the libraries:
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Set DHT pin:
#define DHTPIN 2

// Define SDA and SCL pin for LCD:
#define SDAPin A4 // Data pin
#define SCLPin A5 // Clock pin

// Set DHT type
#define DHTTYPE DHT11   // DHT 11 
// #define DHTTYPE DHT22   // DHT 22  (AM2302)
// #define DHTTYPE DHT21   // DHT 21 (AM2301)

// Initialize DHT sensor for normal 16mhz Arduino:
DHT dht = DHT(DHTPIN, DHTTYPE);

// Connect to LCD via I2C
LiquidCrystal_I2C lcd = LiquidCrystal_I2C(0x27, 16, 2);

// Set Water Atomizer pin:
#define Atomizer A0

// Set Fan pin:
const int RELAY_FAN_PIN = A3;

void setup() {
  // Setup DHT sensor:
  dht.begin();

  // Initiate the LCD:
  lcd.init();
  lcd.backlight();

  // Water Atomizer
  Serial.begin(9600);
  pinMode(Atomizer, OUTPUT);

  // initialize analogue pin 3 as an output.
  pinMode(RELAY_FAN_PIN, OUTPUT);
}

void loop() {
  // Wait a few seconds between measurements:
  delay(2000);

  // Reading temperature or humidity takes about 250ms;
  // Sensor readings may also be up to 2s.

  // Read the humidity in %:
  float h = dht.readHumidity();
  
  // Read the temperature as Celsius:
  float t = dht.readTemperature();
  
  // Print the temperature and the humidity on the LCD:
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(t);
  lcd.print(" " "\xDF" "C");
  
  lcd.setCursor(0, 1);
  lcd.print("Humid: ");
  lcd.print(h);
  lcd.print(" %");


  if (h < 80.00) {
    Serial.println("Atomizer Activated");
    digitalWrite(Atomizer, HIGH);
    digitalWrite(RELAY_FAN_PIN, HIGH);
  }

  else {
    Serial.println("Atomizer Deactivated");
    digitalWrite(Atomizer,LOW);
    digitalWrite(RELAY_FAN_PIN, LOW);
  }
  
}
