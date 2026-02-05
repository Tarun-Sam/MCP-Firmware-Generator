#include <Arduino.h>

// Define GPIO pins
const int ledPin = 2;        // LED connected to GPIO2
const int buzzerPin = 5;     // Buzzer connected to GPIO5
const int adcPin = 34;      // ADC pin connected to water level sensor

// Define water level threshold
const int waterLevelThreshold = 600; // Adjust this value based on your sensor's output

// Serial communication setup
void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
}

void loop() {
  // Read analog value from ADC
  int sensorValue = analogRead(adcPin);

  // Print sensor value to serial monitor
  Serial.print("Sensor Value: ");
  Serial.println(sensorValue);

  // Check if water level exceeds the threshold
  if (sensorValue > waterLevelThreshold) {
    // Turn ON LED and sound buzzer
    digitalWrite(ledPin, HIGH);
    digitalWrite(buzzerPin, HIGH);
    Serial.println("Water level high! LED ON, Buzzer ON");
  } else {
    // Turn OFF LED and stop buzzer
    digitalWrite(ledPin, LOW);
    digitalWrite(buzzerPin, LOW);
    Serial.println("Water level normal. LED OFF, Buzzer OFF");
  }

  // Delay for a short period (e.g., 100ms) to avoid overwhelming the ADC
  delay(100);
}