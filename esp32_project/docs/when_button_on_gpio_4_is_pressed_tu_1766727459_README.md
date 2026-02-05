# ESP32 Code Documentation

## Project Overview
This project is an example of how to use the ESP32 microcontroller to turn on an LED when a button is pressed. The button is connected to GPIO 4 and the LED is connected to GPIO 2. When the button is pressed, the LED will turn on for one second before turning off.

## Hardware Requirements
To run this project, you will need an ESP32 microcontroller board and a button connected to GPIO 4. You will also need an LED connected to GPIO 2. The button should be connected in series with a resistor, as the ESP32 may not be able to handle a direct connection to the input pin.

## Libraries Used
This project uses the Arduino library for the ESP32 board. You will need to have this library installed on your development environment in order to run the code.

## How It Works
The code sets up the button and LED pins as inputs and outputs, respectively. When the button is pressed, the code checks if the input pin is high (i.e., the button is pressed). If it is, the code turns on the LED using the `ledcWrite()` function. The `delay()` function is used to delay the turning off of the LED for one second before detaching the pin.

## Pin Configuration
The button is connected to GPIO 4 and the LED is connected to GPIO 2. Make sure that you have these pins configured correctly on your ESP32 board.

## Troubleshooting
If the LED does not turn on when the button is pressed, check the pin configuration and make sure that everything is connected correctly. If the problem persists, try using a different microcontroller or checking for any firmware issues.