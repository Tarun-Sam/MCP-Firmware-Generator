#include <Arduino.h>

// Define GPIO pins
const int gasSensorPin = 34; // Replace with the actual GPIO pin for your gas sensor
const int buzzerPin = 5;    // Replace with the actual GPIO pin for your buzzer

// Define PWM channel and frequency
const int ledchAnnElec = 0;
const uint32_t ledcPeriod = 1000; 

void setup() {
  Serial.begin(115200);
  pinMode(buzzerPin, OUTPUT);
  ledcSetup(ledchAnnElec, ledcPeriod, 0);
  ledcAttachPin(buzzerPin, ledchAnnElec);
}

void loop() {
  // Read gas sensor value
  int sensorValue = analogRead(gasSensorPin);

  // Print the sensor value to the Serial monitor
  Serial.print("Gas Sensor Value: ");
  Serial.println(sensorValue);

  // Define thresholds for gas levels
  const int highGasThreshold = 700; // Adjust this value based on your sensor's output
  const int lowGasThreshold = 500;  // Adjust this value based on your sensor's output

  // Check if gas level is high
  if (sensorValue > highGasThreshold) {
    // Activate buzzer
    digitalWrite(buzzerPin, HIGH);
    Serial.println("Gas Level High - Buzzer ON");
  } else {
    // Deactivate buzzer
    digitalWrite(buzzerPin, LOW);
    Serial.println("Gas Level Low - Buzzer OFF");
  }

  // Delay for a short period
  delay(100);
}