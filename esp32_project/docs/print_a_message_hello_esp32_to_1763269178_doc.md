
# Hello, ESP32! Example Code

This code demonstrates how to print a message 'Hello, ESP32!' to the serial monitor every 2 seconds using the Arduino IDE.

## Functions Used

* `setup()`: Initializes the serial monitor and sets the baud rate to 115200.
* `loop()`: Prints the message 'Hello, ESP32!' to the serial monitor every 2 seconds using the `Serial.println()` function. The `delay(2000)` function is used to pause execution for 2 seconds between each print.

## Pin Assignments

No pin assignments are required for this example code.

## Usage Examples

1. Upload the code to your ESP32 board and open the serial monitor. You should see the message 'Hello, ESP32!' printed every 2 seconds.

## Parameters

* `Serial.begin(115200)`: Sets the baud rate of the serial communication to 115200 bps.
* `Serial.println("Hello, ESP32!")`: Prints the message 'Hello, ESP32!' to the serial monitor.
* `delay(2000)`: Pauses execution for 2 seconds between each print of the message.

## Troubleshooting

If you are experiencing issues with this example code, try the following:

1. Ensure that your ESP32 board is properly connected to a serial monitor and has power supply.
2. Check the baud rate of your serial monitor matches the one set in `Serial.begin()`.
3. If the issue persists, try uploading the code to a different ESP32 board or changing the delay time between prints.