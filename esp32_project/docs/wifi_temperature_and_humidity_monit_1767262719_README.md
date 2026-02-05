# WiFi temperature and humidity monitor using an ESP32 and a DHT22 sensor that uploads readings to a private ThingSpeak channel every 30 seconds with real-time display on a 128x64 OLED screen

**Auto-generated Documentation**  
*Generated: 2026-01-01 15:48:42*

---

## Table of Contents

1. [Overview](#overview)
2. [Hardware Setup](#hardware-setup-guide)
3. [Pin Configuration](#pin-configuration)
4. [Library Installation](#library-installation-guide)
5. [Code Walkthrough](#code-walkthrough)
6. [Troubleshooting](#troubleshooting-guide)
7. [Safety Information](#safety-warnings)

---

## Overview

This embedded systems project implements: **WiFi temperature and humidity monitor using an ESP32 and a DHT22 sensor that uploads readings to a private ThingSpeak channel every 30 seconds with real-time display on a 128x64 OLED screen**

### Quick Start
1. Install required libraries (see section below)
2. Wire components according to pin guide
3. Upload code to ESP32
4. Open Serial Monitor (115200 baud)
5. Monitor output and verify operation

---

# Hardware Setup Guide

## Project: WiFi temperature and humidity monitor using an ESP32 and a DHT22 sensor that uploads readings to a private ThingSpeak channel every 30 seconds with real-time display on a 128x64 OLED screen

## Overview
This project uses the following hardware components and protocols.

## Hardware Components

### Microcontroller
- ESP32 DevKit V1 (or compatible)
- Operating Voltage: 3.3V
- Input Voltage: 5V via USB or 7-12V via VIN

### Sensors
- Temperature/Humidity Sensor (DHT22/DHT11)

### Actuators/Outputs
- No actuators detected

### Communication Protocols
- I2C
- SPI
- UART
- WiFi

### Additional Components Needed
- USB cable (for programming and power)
- Breadboard and jumper wires
- Pull-up resistors (2x 4.7kΩ) for I2C
- Capacitors (0.1µF ceramic) for power filtering


---

# Pin Configuration

## GPIO Pins Used in This Project

| Variable Name | GPIO Pin | Source |
|---------------|----------|--------|
| DHTPIN | GPIO4 | #define directive |

## ESP32 DevKit V1 Pin Reference

| Function | GPIO | Notes |
|----------|------|-------|
| Boot Button | 0 | Pull-up required, used for boot mode |
| TX (UART0) | 1 | Serial output (avoid using if using Serial) |
| Built-in LED | 2 | Active LOW on most boards |
| RX (UART0) | 3 | Serial input (avoid using if using Serial) |
| SDA (I2C) | 21 | Default I2C data line |
| SCL (I2C) | 22 | Default I2C clock line |
| MOSI (SPI) | 23 | SPI master out, slave in |
| MISO (SPI) | 19 | SPI master in, slave out |
| SCK (SPI) | 18 | SPI clock |
| SS (SPI) | 5 | SPI chip select |
| ADC1 Pins | 32-39 | Analog input capable |
| DAC Pins | 25, 26 | Digital-to-analog capable |
| Touch Pins | 0,2,4,12-15,27,32,33 | Capacitive touch sensing |
| GND | GND | Ground reference |
| 3.3V | 3V3 | 3.3V output (max 600mA) |
| 5V | 5V/VIN | 5V input/output |

**⚠️ CAUTION:**
- GPIO 6-11 are used for internal flash - DO NOT USE
- GPIO 34-39 are input only (no pull-up/pull-down)
- All GPIO pins are 3.3V - NOT 5V tolerant!

## Wiring Best Practices

1. **I2C Connections:** Always use 4.7kΩ pull-up resistors on SDA and SCL
2. **Power Decoupling:** Add 0.1µF capacitors near sensor VCC/GND pins
3. **Wire Length:** Keep sensor wires under 30cm for reliable I2C
4. **Breadboard:** Use quality breadboards with good connections
5. **Polarity:** Double-check VCC/GND before powering on
6. **Current Limiting:** Add resistors to LEDs (220Ω-1kΩ)
7. **Level Shifting:** Use level shifters for 5V sensors


---

# Library Installation Guide

## Required Libraries

This project requires **1** external libraries.

### Method 1: PlatformIO CLI (Recommended)

Open terminal in project directory and run:

```bash
pio lib install "DHT.h"
```

### Method 2: PlatformIO IDE

1. Open PlatformIO sidebar → Libraries
2. Search and install each library:
   1. Search: `DHT.h`
3. Click **Install** for each
4. Restart IDE

### Method 3: platformio.ini Configuration

Add these lines to your `platformio.ini`:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    DHT.h
```

PlatformIO will auto-install libraries on first build.

### Built-in Libraries Used



---

## Code Walkthrough

### Program Structure

#### `void setup()`
Runs **once** when the board powers on or resets.

**Initialization tasks:**
- ✓ Initialize serial communication for debugging
- ✓ Connect to WiFi network
- ✓ Initialize sensors/peripherals

#### `void loop()`
Runs **continuously** after setup() completes.

**Main program flow:**
1. Read sensor data
2. Output data to Serial
5. Wait before next iteration



---

# Troubleshooting Guide

## Compilation Issues

### Error: "Library not found"
**Symptoms:** `fatal error: XXX.h: No such file or directory`

**Solutions:**
1. Install missing library: `pio lib install "library-name"`
2. Check library spelling in #include
3. Verify platformio.ini lib_deps section
4. Clean and rebuild: `pio run --target clean`

### Error: "Undefined reference"
**Symptoms:** `undefined reference to 'functionName'`

**Solutions:**
1. Verify library is installed
2. Check function name spelling
3. Ensure all required #include statements present
4. Rebuild project completely

### Error: "Not enough memory"
**Symptoms:** Code too large for flash/RAM

**Solutions:**
1. Remove debug Serial.println() statements
2. Use F() macro for strings: `Serial.println(F("text"))`
3. Move large strings to PROGMEM
4. Reduce array sizes
5. Optimize loops and variables

## Upload Issues

### Error: "Failed to connect"
**Symptoms:** Cannot upload code to board

**Solutions:**
1. Check USB cable (use data cable, not charge-only)
2. Select correct COM port in PlatformIO
3. Install CH340/CP2102 USB drivers
4. Hold BOOT button while uploading
5. Try different USB port
6. Reset board before upload

### Error: "Timeout waiting for packet header"
**Solutions:**
1. Lower upload speed in platformio.ini:
   ```ini
   upload_speed = 115200
   ```
2. Press and hold BOOT button during upload
3. Reset board and retry immediately

## Runtime Issues

### Issue: Code doesn't execute
**Check:**
1. Serial monitor shows nothing → Check baud rate (115200)
2. LED doesn't blink → Check pin number
3. Sensor doesn't work → Check wiring
4. WiFi doesn't connect → Check SSID/password

**Debug steps:**
```cpp
void setup() {
    Serial.begin(115200);
    Serial.println("\n\n=== Starting ===");
    Serial.println("Testing...");
}
```

### Issue: Sensor reads incorrect values
**Common causes:**
1. **Wiring error** - Check VCC, GND, signal pins
2. **Power issues** - Use external power for multiple sensors
3. **I2C address conflict** - Run I2C scanner
4. **Timing issues** - Add delays after sensor init
5. **Pull-up resistors** - I2C needs 4.7kΩ resistors

**I2C Scanner Code:**
```cpp
#include <Wire.h>

void setup() {
    Wire.begin();
    Serial.begin(115200);
    Serial.println("I2C Scanner");
}

void loop() {
    for(byte i = 8; i < 120; i++) {
        Wire.beginTransmission(i);
        if(Wire.endTransmission() == 0) {
            Serial.print("Found: 0x");
            Serial.println(i, HEX);
        }
    }
    delay(5000);
}
```

### Issue: Board resets randomly
**Causes:**
1. Insufficient power (use 2A+ USB adapter)
2. Brown-out detection triggered
3. Watchdog timer reset
4. Code crashes (check array bounds)

**Solutions:**
1. Add `esp_task_wdt_reset()` in long loops
2. Use external 5V power supply
3. Add capacitors (100µF) on power rails
4. Check for infinite loops

## WiFi Issues

### Cannot connect to WiFi
**Debug code:**
```cpp
WiFi.begin("SSID", "password");
Serial.print("Connecting");
while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
}
Serial.println("\nConnected!");
Serial.println(WiFi.localIP());
```

**Solutions:**
1. Check SSID and password spelling
2. Verify WiFi is 2.4GHz (not 5GHz)
3. Check signal strength
4. Disable MAC filtering on router
5. Try static IP instead of DHCP

### Random WiFi disconnects
**Solutions:**
1. Increase WiFi TX power:
   ```cpp
   WiFi.setTxPower(WIFI_POWER_19_5dBm);
   ```
2. Add reconnection logic:
   ```cpp
   if(WiFi.status() != WL_CONNECTED) {
       WiFi.reconnect();
   }
   ```
3. Reduce distance to router
4. Check for interference

## Safety Warnings

⚠️ **CRITICAL - READ BEFORE POWERING ON:**

1. **Voltage Limits**
   - ESP32 GPIO pins are 3.3V ONLY
   - Connecting 5V will **PERMANENTLY DAMAGE** the chip
   - Use level shifters for 5V devices

2. **Current Limits**
   - Maximum 12mA per GPIO pin
   - Maximum 40mA total for all pins
   - Use transistors/MOSFETs for high-current loads

3. **Power Supply**
   - USB provides max 500mA (often less)
   - Multiple sensors need external power
   - Use 5V/2A+ adapter for motors/servos

4. **Static Electricity**
   - Touch grounded metal before handling board
   - Use anti-static mat/wrist strap
   - Store in anti-static bag

5. **Short Circuits**
   - Double-check all connections
   - Keep metal objects away from powered board
   - Use insulated workspace

## Getting Help

If issues persist:

1. **Check Serial Monitor**
   - Baud rate: 115200
   - Look for error messages
   - Add debug print statements

2. **Search Online**
   - Arduino Forums
   - ESP32 subreddit
   - Stack Overflow

3. **Check Datasheets**
   - Sensor specifications
   - Pin configurations
   - Communication protocols

4. **Use Multimeter**
   - Verify power voltage (3.3V/5V)
   - Check continuity
   - Test for shorts

5. **Minimal Test Code**
   - Strip down to basics
   - Test one component at a time
   - Isolate the problem


---

## Additional Resources

### Official Documentation
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [Arduino Language Reference](https://www.arduino.cc/reference/en/)
- [PlatformIO Documentation](https://docs.platformio.org/)
- [ESP32 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)

### Community
- [ESP32 Forum](https://www.esp32.com/)
- [Arduino Forum](https://forum.arduino.cc/)
- [PlatformIO Community](https://community.platformio.org/)

### Tools
- [Serial Monitor](https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html)
- [I2C Scanner Tool](https://playground.arduino.cc/Main/I2cScanner/)
- [ESP32 Pinout Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)

---

## License

This code and documentation are provided as-is for educational purposes.

**Support:** For issues or questions, consult the troubleshooting section above.

---

*Documentation auto-generated by MCP Documentation Generator (Phase 7)*
