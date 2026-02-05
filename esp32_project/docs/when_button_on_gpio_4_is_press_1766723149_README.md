
# Project Overview
This ESP32 firmware code is designed to turn on an LED on GPIO 2 for 1 second when button on GPIO 4 is pressed.

# Hardware Requirements
* ESP32 board
* Button on GPIO 4
* LED on GPIO 2

# Libraries Used
* Arduino (version)

# How It Works
The code uses the `digitalRead()` function to read the state of button on GPIO 4 and checks if it is HIGH. If so, it turns on the LED on GPIO 2 using the `digitalWrite()` function and delays for 1 second using the `delay()` function before turning off the LED using the `digitalWrite()` function again.

# Pin Configuration
* Button on GPIO 4
* LED on GPIO 2

# Troubleshooting Tips
* Check if button is correctly connected to GPIO 4 and LED is correctly connected to GPIO 2.
* Make sure the ESP32 board has power and the serial monitor is open before uploading the code.
* If the LED does not turn on, check the delay function and make sure it is set to 1 second.