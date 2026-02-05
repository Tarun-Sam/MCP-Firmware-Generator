#include <Arduino.h>

int ledPin = 13; // Pin connected to the LED

void setup() {
  pinMode(ledPin, OUTPUT); // Set the LED pin as an output
}

void loop() {
  digitalWrite(ledPin, HIGH); // Turn the LED on
  delay(1000); // Wait for 1 second
  digitalWrite(ledPin, LOW); // Turn the LED off
  delay(1000); // Wait for another 1 second
}