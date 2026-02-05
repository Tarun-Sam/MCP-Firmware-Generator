#!/usr/bin/env python3
"""
MCP Client - Orchestrates calls to all MCP servers
Phase 9: Thin delegation layer - delegates to specialized servers
"""

import json
import re
from typing import Dict, List, Optional

# Import the refactored code quality server
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_servers'))

try:
    from code_quality_server import CodeQualityAnalyzer, BOARD_SPECS
    HAS_QUALITY_SERVER = True
except ImportError:
    HAS_QUALITY_SERVER = False
    print("⚠️ Code Quality Server not available")

class MCPClient:
    """Client for coordinating MCP server calls - REFACTORED."""
    
    def __init__(self, server_config_path: str = "config.json"):
        self.config_path = server_config_path
        self.servers = {}
        self.processes = {}
        
        # Initialize code quality analyzer
        if HAS_QUALITY_SERVER:
            self.quality_analyzer = CodeQualityAnalyzer()
        else:
            self.quality_analyzer = None
        
        print("✅ MCPClient initialized (Phase 9 - Refactored)")
    
    # ============================================================================
    # HARDWARE DATABASE METHODS (Unchanged)
    # ============================================================================
    
    def get_board_specs(self, board: str = "esp32dev") -> Dict:
        """Get board specifications from hardware database."""
        boards = {
            "esp32dev": {
                "name": "ESP32 DevKit V1",
                "flash_mb": 4,
                "ram_kb": 520,
                "gpio_pins": 40,
                "adc_channels": 18,
                "uart_ports": 3,
                "i2c_ports": 2,
                "spi_ports": 3,
                "pwm_channels": 16
            },
            "esp32s3": {
                "name": "ESP32-S3",
                "flash_mb": 8,
                "ram_kb": 1507,
                "gpio_pins": 49,
                "adc_channels": 20,
                "uart_ports": 3,
                "i2c_ports": 1,
                "spi_ports": 4,
                "pwm_channels": 16
            },
            "esp32c3": {
                "name": "ESP32-C3",
                "flash_mb": 4,
                "ram_kb": 400,
                "gpio_pins": 22,
                "adc_channels": 6,
                "uart_ports": 2,
                "i2c_ports": 1,
                "spi_ports": 2,
                "pwm_channels": 6
            }
        }
        
        if board in boards:
            return boards[board]
        return boards["esp32dev"]
    
    def get_gpio_for_purpose(self, board: str, purpose: str) -> List[int]:
        """Get GPIO pins for specific purpose."""
        gpio_map = {
            "led": [2, 4, 5, 13, 14, 15, 25, 26, 27, 32, 33],
            "button": [0, 12, 13, 14, 15, 25, 26, 27, 32, 33],
            "pwm": list(range(0, 40)),
            "adc": [32, 33, 34, 35, 36, 39],
            "i2c": [21, 22],
            "spi": [5, 18, 19, 23],
            "uart": [1, 3, 16, 17]
        }
        
        return gpio_map.get(purpose, [])
    
    def get_default_uart(self, board: str) -> Dict:
        """Get default UART configuration."""
        configs = {
            "esp32dev": {"rx": 3, "tx": 1, "baud": 115200},
            "esp32s3": {"rx": 44, "tx": 43, "baud": 115200},
            "esp32c3": {"rx": 20, "tx": 21, "baud": 115200}
        }
        return configs.get(board, configs["esp32dev"])
    
    def get_default_i2c(self, board: str) -> Dict:
        """Get default I2C configuration."""
        configs = {
            "esp32dev": {"sda": 21, "scl": 22, "freq": 100000},
            "esp32s3": {"sda": 8, "scl": 9, "freq": 100000},
            "esp32c3": {"sda": 8, "scl": 9, "freq": 100000}
        }
        return configs.get(board, configs["esp32dev"])
    
    # ============================================================================
    # LIBRARY MANAGER METHODS (Unchanged)
    # ============================================================================
    
    def scan_code_libraries(self, code: str) -> List[str]:
        """Extract #include statements from code."""
        pattern = r'#include\s+[<"]([a-zA-Z0-9_./\-]+\.h)[>"]'
        matches = re.findall(pattern, code, re.IGNORECASE)
        return list(set(matches))
    
    def get_library_mapping(self) -> Dict[str, str]:
        """Return library mapping."""
        return {
            "DHT.h": "adafruit/DHT-sensor-library",
            "Adafruit_Sensor.h": "adafruit/Adafruit-Unified-Sensor",
            "OneWire.h": "paulstoffregen/OneWire",
            "DallasTemperature.h": "milesburton/DallasTemperature",
            "Wire.h": "builtin",
            "SPI.h": "builtin",
            "WiFi.h": "builtin",
            "WebServer.h": "builtin",
            "HTTPClient.h": "builtin",
            "EEPROM.h": "builtin",
            "PubSubClient.h": "knolleary/PubSubClient",
            "ArduinoJson.h": "bblanchon/ArduinoJson",
            "Servo.h": "builtin",
            "NeoPixel.h": "adafruit/Adafruit-NeoPixel",
            "AsyncTCP.h": "me-no-dev/AsyncTCP",
            "ESPAsyncWebServer.h": "me-no-dev/ESPAsyncWebServer",
            "WiFiManager.h": "tzapu/WiFiManager",
            "LiquidCrystal_I2C.h": "mathertel/LiquidCrystal_I2C",
            "SSD1306.h": "adafruit/Adafruit-SSD1306",
            "BluetoothSerial.h": "builtin",
            "BLEDevice.h": "builtin",
        }
    
    def analyze_libraries(self, code: str, board: str = "esp32dev") -> Dict:
        """Analyze all libraries in code."""
        includes = self.scan_code_libraries(code)
        lib_map = self.get_library_mapping()
        
        external_libs = []
        builtin_libs = []
        unknown_libs = []
        
        for header in includes:
            lib_name = lib_map.get(header, "unknown")
            
            if lib_name == "builtin":
                builtin_libs.append({"header": header, "library": "builtin"})
            elif lib_name == "unknown":
                unknown_libs.append({"header": header})
            else:
                external_libs.append({
                    "header": header,
                    "library": lib_name,
                    "install_cmd": f"pio lib install \"{lib_name}\""
                })
        
        return {
            "board": board,
            "total_includes": len(includes),
            "external_libraries": external_libs,
            "builtin_libraries": builtin_libs,
            "unknown_libraries": unknown_libs,
            "external_count": len(external_libs),
            "builtin_count": len(builtin_libs),
            "unknown_count": len(unknown_libs)
        }
    
    # ============================================================================
    # CODE QUALITY METHODS - REFACTORED (Delegation to Server)
    # ============================================================================
    
    def analyze_code_quality(self, code: str, board: str = "esp32dev") -> Dict:
        """
        Analyze code quality - DELEGATES to code_quality_server.py
        
        This is now a thin wrapper that delegates ALL analysis logic
        to the specialized code quality server.
        """
        
        if HAS_QUALITY_SERVER and self.quality_analyzer:
            # Delegate to the specialized server
            return self.quality_analyzer.analyze(code, board)
        else:
            # Fallback mode when server unavailable
            return self._fallback_quality_analysis(code, board)
    
    def _fallback_quality_analysis(self, code: str, board: str) -> Dict:
        """
        Minimal fallback analysis when code quality server unavailable.
        Returns simplified structure compatible with main.py API.
        """
        
        issues = []
        warnings = []
        score = 100
        
        # Basic checks
        if "void setup()" not in code:
            issues.append("Missing setup() function")
            score -= 20
        
        if "void loop()" not in code:
            issues.append("Missing loop() function")
            score -= 20
        
        if "Serial.begin" not in code:
            warnings.append("No Serial.begin() - debugging difficult")
            score -= 5
        
        # Estimate memory
        code_size_kb = len(code) / 1024
        board_specs = self.get_board_specs(board)
        ram_kb = board_specs.get("ram_kb", 520)
        usage_percent = (code_size_kb / ram_kb) * 100
        
        return {
            "quality_score": max(0, score),
            "issues": issues,
            "warnings": warnings,
            "code_lines": len(code.split('\n')),
            "code_size_kb": round(code_size_kb, 2),
            "estimated_ram_usage_percent": round(usage_percent, 1),
            "memory_status": "critical" if usage_percent > 80 else "warning" if usage_percent > 50 else "good",
            "severity": "critical" if score < 50 else "high" if score < 75 else "medium" if score < 90 else "excellent",
            "summary": f"Fallback analysis: {len(issues)} issues, {len(warnings)} warnings (score: {score}/100)"
        }
    
    # ============================================================================
    # COMBINED ANALYSIS (Updated to use refactored quality)
    # ============================================================================
    
    def full_analysis(self, code: str, board: str = "esp32dev") -> Dict:
        """Run all analyses and combine results."""
        return {
            "board_specs": self.get_board_specs(board),
            "libraries": self.analyze_libraries(code, board),
            "code_quality": self.analyze_code_quality(code, board),  # Now delegates!
            "default_uart": self.get_default_uart(board),
            "default_i2c": self.get_default_i2c(board)
        }
    
    def cleanup(self):
        """Clean up resources."""
        for name, proc in self.processes.items():
            try:
                proc.terminate()
            except:
                pass
        print("✅ MCPClient cleanup complete")

# ============================================================================
# TEST MODE
# ============================================================================

if __name__ == "__main__":
    import json
    
    print("\n" + "="*70)
    print("MCP Client - Refactored Test (Phase 9)")
    print("="*70 + "\n")
    
    client = MCPClient()
    
    sample_code = """
#include <WiFi.h>
#include <DHT.h>
#include <Wire.h>
#include <ArduinoJson.h>

#define LED_PIN 2
char largeBuffer[2000];

void setup() {
    Serial.begin(115200);
    Wire.begin();
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    float temp = 25.5;
    Serial.println(temp);
    delay(5000);
}
"""
    
    print("📊 Testing on ESP32-C3 (Low RAM board)...")
    result = client.analyze_code_quality(sample_code, "esp32c3")
    
    print(f"\n✅ Quality Score: {result['quality_score']}/100")
    print(f"📝 {result['summary']}")
    print(f"💾 Memory: {result['estimated_ram_usage_percent']}% ({result['memory_status']})")
    
    if 'issues_by_severity' in result:
        print(f"\n🚨 Critical Issues: {len(result['issues_by_severity']['critical'])}")
        print(f"⚠️  High Issues: {len(result['issues_by_severity']['high'])}")
        print(f"ℹ️  Medium Issues: {len(result['issues_by_severity']['medium'])}")
    
    print("\n" + "="*70)
    print("✅ Refactored MCP Client working!")