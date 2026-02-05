
## Function Descriptions

1. `setup()`: This function initializes the serial communication channel for debugging purposes and sets up the GPIO pins used in the program.
2. `loop()`: This function continuously checks the button state using the `digitalRead()` function and turns on the LED if the button is pressed. The LED is turned off after 1 second using the `delay()` function.

## Parameters

1. `ledPin`: This parameter defines the GPIO pin number for the LED. In this case, it is set to 2.
2. `DHTPIN`: This parameter defines the GPIO pin number for the button. In this case, it is set to 4.
3. `DHT22`: This parameter defines the DHT sensor type and pin number used in the program. It is set to 22.

## Usage Examples

1. To turn on the LED when the button is pressed:
```cpp
void loop() {
  // Check button state
  if (digitalRead(DHTPIN) == LOW) {
    // Button is pressed, turn on LED for 1 second
    digitalWrite(ledPin, HIGH);
    delay(1000);
    digitalWrite(ledPin, LOW);
  }
}
```
2. To turn off the LED when the button is not pressed:
```cpp
void loop() {
  // Check button state
  if (digitalRead(DHTPIN) == HIGH) {
    // Button is not pressed, turn off LED
    digitalWrite(ledPin, LOW);
  }
}
```
## Pin Assignments

1. `ledPin`: This pin is assigned to GPIO 2 for controlling the LED.
2. `DHTPIN`: This pin is assigned to GPIO 4 for reading the button state.