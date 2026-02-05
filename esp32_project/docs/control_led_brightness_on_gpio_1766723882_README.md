
# Project Overview
This project is an example of using the ESP32 microcontroller to control the brightness of an LED connected to GPIO 18. The code uses the `ledcSetup` and `ledcAttachPin` functions from the Arduino core library to set up the PWM for the LED and attach it to GPIO pin 18, respectively.

# Hardware Requirements
* ESP32 microcontroller board
* LED connected to GPIO 18

# Libraries Used
* Arduino core library (version x)

# How It Works
The `ledcSetup` function sets up the PWM for the LED, specifying the frequency and resolution. The `ledcAttachPin` function attaches the LED to GPIO pin 18, which is where it will be controlled by the code. The `ledcWrite` function sets the brightness of the LED to a value between 0 and 255, with 0 being the minimum brightness and 255 being the maximum.

# Pin Configuration
The LED is attached to GPIO pin 18 using the `ledcAttachPin` function.

# Troubleshooting Tips
If the LED does not turn on, check that the GPIO pin is configured correctly and that the PWM frequency and resolution are set correctly. If the LED does not change brightness, check that the `ledcWrite` function is being called correctly and that the value passed to it is between 0 and 255.