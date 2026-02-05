#include <Arduino.h>

// Define GPIO pins
const int gasSensorPin = 34; // Replace with the actual GPIO pin of your gas sensor
const int buzzerPin = 2;   // Replace with the actual GPIO pin of your buzzer

// LEDC setup for PWM control of the buzzer
const int ledcChannel = 0;
const int ledcMap = 0;

void setup() {
  Serial.begin(115200);
  pinMode(gasSensorPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  ledcSetup(ledcChannel, ledcMap, 10); // Adjust PWM frequency as needed
  ledcAttachPin(buzzerPin, ledcChannel);
}

void loop() {
  // Read gas sensor value
  int gasValue = digitalRead(gasSensorPin);

  // Buzzer control based on gas sensor value
  if (gasValue == LOW) {
    // Gas detected - activate buzzer
    digitalWrite(buzzerPin, HIGH);
    Serial.println("Gas detected! Buzzer ON");
  } else {
    // No gas detected - deactivate buzzer
    digitalWrite(buzzerPin, LOW);
    Serial.println("No gas detected. Buzzer OFF");
  }

  delay(100); // Short delay to prevent overwhelming the system
}