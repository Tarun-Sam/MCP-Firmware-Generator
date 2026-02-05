
# LEDC PWM Generation for Embedded Systems

This code generates a 1kHz PWM signal with 25% duty cycle on GPIO 18 using the `ledc` library in Arduino.

## Functions

### ledcSetup(channel, frequency, resolution)

* `channel`: The PWM channel to use (0-7)
* `frequency`: The desired PWM frequency in Hz
* `resolution`: The desired PWM resolution (8 or 10 bits)

Sets up the specified PWM channel with the given parameters.

### ledcAttachPin(pin, channel)

* `pin`: The pin to attach to the PWM channel (GPIO number)
* `channel`: The PWM channel to attach to the pin (0-7)

Attaches a pin to the specified PWM channel.

### ledcWrite(channel, duty)

* `channel`: The PWM channel to write to (0-7)
* `duty`: The duty cycle of the PWM signal as an integer value between 0 and 255

Writes a value to the specified PWM channel.

## Usage Examples

### Generating a 1kHz PWM signal with 25% duty cycle on GPIO 18

```cpp
ledcSetup(0, 1000, 8);
ledcAttachPin(18, 0);
ledcWrite(0, 64);
```

## Pin Assignments

* GPIO 18: Output pin for the PWM signal.