#!/usr/bin/env python3
"""
Library Manager MCP Server
Scans code for dependencies, detects required libraries, checks compatibility
"""

import re
import json
from typing import List, Dict, Optional

# Try importing MCP SDK
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠ MCP not installed. Running in standalone mode.")

# ============================================================================
# LIBRARY MAPPING - Your existing mapping from main.py
# ============================================================================

LIBRARY_MAPPING = {
    # Sensor Libraries
    "DHT.h": "adafruit/DHT-sensor-library",
    "Adafruit_Sensor.h": "adafruit/Adafruit-Unified-Sensor",
    "OneWire.h": "paulstoffregen/OneWire",
    "DallasTemperature.h": "milesburton/DallasTemperature",
    "BMP085.h": "adafruit/Adafruit-BMP085-Library",
    "MPU6050.h": "jrowberg/MPU6050",
    "BMP280.h": "adafruit/Adafruit-BMP280-Library",
    "INA219.h": "adafruit/Adafruit-INA219",
    "ADXL345.h": "adafruit/Adafruit-ADXL345",
    "HTU21D.h": "sparkfun/SparkFun-HTU21D-Humidity-and-Temperature-Sensor",
    "BH1750.h": "claws/BH1750",
    "TSL2561.h": "adafruit/Adafruit-TSL2561",
    "VL53L0X.h": "pololu/VL53L0X",
    "MLX90614.h": "adafruit/Adafruit-MLX90614-Library",
    
    # Display Libraries
    "LiquidCrystal_I2C.h": "mathertel/LiquidCrystal_I2C",
    "SSD1306.h": "adafruit/Adafruit-SSD1306",
    "TM1637.h": "avishorp/TM1637",
    "Adafruit_ST7735.h": "adafruit/Adafruit-ST7735-Library",
    "Adafruit_ILI9341.h": "adafruit/Adafruit-ILI9341",
    "GxEPD.h": "ZinggJM/GxEPD",
    "MAX7219.h": "sparkfun/SparkFun-LED-Array-8x8",
    
    # LED & Light Control
    "ws2812b.h": "kitesurfer1404/WS2812FX",
    "NeoPixel.h": "adafruit/Adafruit-NeoPixel",
    
    # Communication Libraries
    "PubSubClient.h": "knolleary/PubSubClient",
    "AsyncTCP.h": "me-no-dev/AsyncTCP",
    "ESPAsyncWebServer.h": "me-no-dev/ESPAsyncWebServer",
    "WiFiManager.h": "tzapu/WiFiManager",
    "LoRa.h": "sandeepmistry/arduino-LoRa",
    "RH_RF95.h": "sparkfun/RadioHead",
    
    # Data & Storage
    "ArduinoJson.h": "bblanchon/ArduinoJson",
    
    # Motor Control
    "Servo.h": "builtin",
    "ESP32Servo.h": "madhephaestus/ESP32Servo",
    "AccelStepper.h": "mike-matera/AccelStepper",
    
    # Timing
    "NTPClient.h": "taranais/NTPClient",
    "TimeLib.h": "PaulStoffregen/Time",
    
    # Communication Protocols
    "CAN.h": "sandeepmistry/CAN",
    
    # Built-in Headers
    "BluetoothSerial.h": "builtin",
    "BLEDevice.h": "builtin",
    "LittleFS.h": "builtin",
    "SPIFFS.h": "builtin",
    "SD.h": "builtin",
    "FS.h": "builtin",
    "SoftwareSerial.h": "builtin",
    "Arduino.h": "builtin",
    "Wire.h": "builtin",
    "SPI.h": "builtin",
    "WiFi.h": "builtin",
    "WebServer.h": "builtin",
    "HTTPClient.h": "builtin",
    "EEPROM.h": "builtin",
    "Serial.h": "builtin",
    "pins_arduino.h": "builtin",
    "esp_wifi.h": "builtin",
    "esp_now.h": "builtin",
    "nvs_flash.h": "builtin",
    "driver/gpio.h": "builtin",
    "driver/adc.h": "builtin",
    "driver/uart.h": "builtin",
    "driver/ledc.h": "builtin",
}

# Library categories for context
LIBRARY_CATEGORIES = {
    "sensor": ["DHT", "Adafruit_Sensor", "OneWire", "DallasTemperature", "BMP", "MPU6050"],
    "display": ["SSD1306", "LiquidCrystal", "ST7735", "ILI9341", "GxEPD", "TM1637"],
    "communication": ["PubSubClient", "WiFi", "LoRa", "RadioHead", "WiFiManager"],
    "led": ["NeoPixel", "WS2812", "MAX7219"],
    "data": ["ArduinoJson"],
    "motor": ["Servo", "AccelStepper"],
    "storage": ["LittleFS", "SPIFFS", "SD", "EEPROM"],
    "builtin": ["Arduino", "Wire", "SPI", "Serial", "WebServer", "HTTPClient"]
}

# ============================================================================
# LIBRARY COMPATIBILITY DATABASE
# ============================================================================

LIBRARY_COMPATIBILITY = {
    "esp32dev": {
        "compatible": list(LIBRARY_MAPPING.keys()),
        "tested": [
            "DHT.h", "Wire.h", "SPI.h", "WiFi.h", "PubSubClient.h",
            "Servo.h", "NeoPixel.h", "ArduinoJson.h", "SSD1306.h"
        ],
        "incompatible": []
    },
    "esp32s3": {
        "compatible": list(LIBRARY_MAPPING.keys()),
        "tested": [
            "DHT.h", "Wire.h", "SPI.h", "WiFi.h", "PubSubClient.h",
            "NeoPixel.h", "ArduinoJson.h", "SSD1306.h"
        ],
        "incompatible": []
    },
    "esp32c3": {
        "compatible": list(LIBRARY_MAPPING.keys()),
        "tested": [
            "DHT.h", "Wire.h", "WiFi.h", "ArduinoJson.h", "SSD1306.h"
        ],
        "incompatible": []
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_includes_from_code(code: str) -> List[str]:
    """Extract all #include statements from code."""
    includes = []
    include_pattern = r'#include\s+[<"]([a-zA-Z0-9_./\-]+\.h)[>"]'
    matches = re.findall(include_pattern, code, re.IGNORECASE)
    
    for match in matches:
        header = match.strip()
        if header and header not in includes:
            includes.append(header)
    
    return includes

def get_library_info(header: str) -> Dict:
    """Get library name and info for a header file."""
    library = LIBRARY_MAPPING.get(header, "unknown")
    
    is_builtin = library == "builtin"
    needs_installation = not is_builtin and library != "unknown"
    
    # Find category
    category = "unknown"
    for cat, libs in LIBRARY_CATEGORIES.items():
        if any(lib.lower() in header.lower() for lib in libs):
            category = cat
            break
    
    return {
        "header": header,
        "library": library,
        "is_builtin": is_builtin,
        "needs_installation": needs_installation,
        "category": category
    }

def check_board_compatibility(library: str, board: str) -> Dict:
    """Check if library is compatible with board."""
    if board not in LIBRARY_COMPATIBILITY:
        return {"compatible": None, "reason": f"Board '{board}' not in database"}
    
    board_compat = LIBRARY_COMPATIBILITY[board]
    
    # Check if header is in library
    header_for_lib = None
    for h, lib in LIBRARY_MAPPING.items():
        if lib == library:
            header_for_lib = h
            break
    
    if not header_for_lib:
        return {"compatible": False, "reason": "Library not found in mapping"}
    
    if header_for_lib in board_compat["incompatible"]:
        return {
            "compatible": False,
            "reason": f"Library explicitly incompatible with {board}",
            "board": board
        }
    
    if header_for_lib in board_compat["compatible"]:
        is_tested = header_for_lib in board_compat["tested"]
        return {
            "compatible": True,
            "board": board,
            "tested": is_tested,
            "confidence": "high" if is_tested else "medium"
        }
    
    return {"compatible": False, "reason": "Library not in compatibility list"}

def get_installation_command(library: str) -> str:
    """Get PlatformIO installation command for library."""
    if library == "builtin":
        return "# Built-in, no installation needed"
    
    # Extract simple library name
    simple_name = library.split('/')[-1]
    return f"pio lib install \"{library}\" # or: pio lib install {simple_name}"

# ============================================================================
# MCP SERVER SETUP
# ============================================================================

if HAS_MCP:
    server = Server("library-manager")
else:
    server = None

# ============================================================================
# MCP TOOL REGISTRATION
# ============================================================================

if HAS_MCP:
    @server.list_tools()
    async def list_tools():
        """List available tools."""
        return [
            Tool(
                name="scan_code_dependencies",
                description="Scan code for #include statements and extract library names",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "C/C++ source code to analyze"
                        }
                    },
                    "required": ["code"]
                }
            ),
            Tool(
                name="get_library_info",
                description="Get library name and installation info for a header file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "header": {
                            "type": "string",
                            "description": "Header file name (e.g., 'DHT.h')"
                        }
                    },
                    "required": ["header"]
                }
            ),
            Tool(
                name="check_board_compatibility",
                description="Check if a library is compatible with a board",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "library": {"type": "string", "description": "Library name"},
                        "board": {"type": "string", "description": "Board ID"}
                    },
                    "required": ["library", "board"]
                }
            ),
            Tool(
                name="get_installation_command",
                description="Get PlatformIO installation command for a library",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "library": {"type": "string", "description": "Library name"}
                    },
                    "required": ["library"]
                }
            ),
            Tool(
                name="analyze_dependencies",
                description="Analyze code and return all dependencies with installation info",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Source code"},
                        "board": {
                            "type": "string",
                            "description": "Target board for compatibility check"
                        }
                    },
                    "required": ["code", "board"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Execute tool calls."""
        
        if name == "scan_code_dependencies":
            code = arguments.get("code", "")
            includes = extract_includes_from_code(code)
            result = {
                "includes": includes,
                "count": len(includes),
                "headers_found": includes
            }
        
        elif name == "get_library_info":
            header = arguments.get("header", "")
            result = get_library_info(header)
        
        elif name == "check_board_compatibility":
            library = arguments.get("library", "")
            board = arguments.get("board", "esp32dev")
            result = check_board_compatibility(library, board)
        
        elif name == "get_installation_command":
            library = arguments.get("library", "")
            result = {
                "library": library,
                "command": get_installation_command(library)
            }
        
        elif name == "analyze_dependencies":
            code = arguments.get("code", "")
            board = arguments.get("board", "esp32dev")
            
            includes = extract_includes_from_code(code)
            dependencies = []
            
            for header in includes:
                lib_info = get_library_info(header)
                compat = check_board_compatibility(lib_info["library"], board)
                
                dependencies.append({
                    "header": header,
                    "library": lib_info["library"],
                    "is_builtin": lib_info["is_builtin"],
                    "category": lib_info["category"],
                    "compatible": compat.get("compatible", False),
                    "needs_installation": lib_info["needs_installation"]
                })
            
            result = {
                "board": board,
                "total_includes": len(includes),
                "dependencies": dependencies,
                "external_libraries": [d for d in dependencies if d["needs_installation"]],
                "builtin_libraries": [d for d in dependencies if d["is_builtin"]],
                "external_count": len([d for d in dependencies if d["needs_installation"]])
            }
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

# ============================================================================
# STANDALONE TEST MODE
# ============================================================================

async def run_mcp_server():
    """Run the MCP server via stdio."""
    if not HAS_MCP:
        print("❌ MCP SDK not installed. Install with: pip install mcp")
        return
    
    from mcp.server.stdio import stdio_server
    
    print("✓ Library Manager MCP Server starting...")
    print("  Ready to analyze code dependencies")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

# ============================================================================
# MAIN / TEST MODE
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    if HAS_MCP:
        print("\n" + "="*70)
        print("📚 Library Manager MCP Server")
        print("="*70)
        asyncio.run(run_mcp_server())
    else:
        # Test mode: Show what the server would return
        print("\n" + "="*70)
        print("📚 Library Manager Server (Test Mode - No MCP)")
        print("="*70)
        
        # Test 1: Scan dependencies
        sample_code = """
#include <WiFi.h>
#include <DHT.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

void setup() {
    Serial.begin(115200);
}

void loop() {
    delay(1000);
}
"""
        
        print("\n📋 Test 1: Scan Code Dependencies")
        print("-" * 70)
        includes = extract_includes_from_code(sample_code)
        print(f"Found {len(includes)} includes: {includes}")
        
        print("\n📋 Test 2: Get Library Info")
        print("-" * 70)
        for header in includes[:3]:
            info = get_library_info(header)
            print(json.dumps(info, indent=2))
        
        print("\n📋 Test 3: Check Board Compatibility")
        print("-" * 70)
        compat = check_board_compatibility("adafruit/DHT-sensor-library", "esp32dev")
        print(json.dumps(compat, indent=2))
        
        print("\n📋 Test 4: Full Analysis")
        print("-" * 70)
        analysis = {
            "code": sample_code[:50] + "...",
            "board": "esp32dev",
            "includes": includes,
            "external_libs": []
        }
        
        for header in includes:
            info = get_library_info(header)
            if info["needs_installation"]:
                analysis["external_libs"].append({
                    "header": header,
                    "library": info["library"],
                    "command": get_installation_command(info["library"])
                })
        
        print(json.dumps(analysis, indent=2))
        print("\n✓ All tests completed!")
