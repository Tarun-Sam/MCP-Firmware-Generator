#include <DHT.h>

#define DHTPIN 25 // digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22 (AM2302)

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // read the value from the DHT sensor:
  float temperature = dht.readTemperature();
  Serial.println("Temperature: " + String(temperature) + "°C");
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}