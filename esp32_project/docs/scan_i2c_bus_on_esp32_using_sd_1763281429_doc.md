
---

### I2C Bus Scanning on ESP32

The code below scans the I2C bus on ESP32 using SDA: GPIO 21 and SCL: GPIO 22, detecting all connected device addresses and printing them to serial.
```cpp
#include <Arduino.h>
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // SDA=21, SCL=22
}

void loop() {
  for (int address = 1; address < 0x7F; address++) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      Serial.print("0x");
      Serial.println(address, HEX);
    }
  }
}
```
---

### Functions

* `setup()`: Initializes the serial port and starts the I2C bus on ESP32 using SDA: GPIO 21 and SCL: GPIO 22.
* `loop()`: Loops through all possible device addresses (0x0 to 0x7F) and checks if each address is connected to a device by sending a start condition, followed by the address, and ending with a stop condition. If the address is connected to a device, it prints the address to serial in hexadecimal format.

---

### Parameters

* `Serial`: The serial port used for printing output.
* `Wire`: The I2C bus on ESP32 using SDA: GPIO 21 and SCL: GPIO 22.

---

### Usage Examples

Example 1: Scanning all connected device addresses on ESP32 using SDA: GPIO 21 and SCL: GPIO 22.
```cpp
void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // SDA=21, SCL=22
}

void loop() {
  for (int address = 1; address < 0x7F; address++) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      Serial.print("0x");
      Serial.println(address, HEX);
    }
  }
}
```
---

### Pin Assignments

* SDA: GPIO 21
* SCL: GPIO 22