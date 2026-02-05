#!/usr/bin/env python3
"""
Hardware Database MCP Server
Provides board specifications, GPIO mappings, and peripheral configs
"""

import json
import sys
from typing import Optional

# Try importing MCP SDK
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠ MCP not installed. Running in standalone mode.")

# ============================================================================
# BOARD DATABASE - Complete Hardware Specifications
# ============================================================================

BOARD_DATABASE = {
    "esp32dev": {
        "id": "esp32dev",
        "name": "ESP32 DevKit V1",
        "manufacturer": "Espressif",
        "platform": "espressif32",
        "framework": "arduino",
        "specs": {
            "flash_size": 4194304,      # 4MB in bytes
            "flash_size_mb": 4,
            "ram_size": 520192,         # 520KB SRAM
            "ram_size_kb": 520,
            "cpu": "Dual-core Tensilica Xtensa 32-bit LX6",
            "cpu_frequency": "160MHz or 240MHz"
        },
        "gpio": {
            "total_pins": 40,
            "available_pins": list(range(0, 40)),
            "adc_pins": [32, 33, 34, 35, 36, 39],
            "dac_pins": [25, 26],
            "pwm_pins": list(range(0, 40)),
            "spi_pins": [5, 18, 19, 23],
            "i2c_pins": [21, 22],
            "uart_pins": [[1, 3], [16, 17], [14, 13]]
        },
        "peripherals": {
            "uart": {
                "count": 3,
                "default": {"number": 0, "rx": 3, "tx": 1, "baud": 115200}
            },
            "i2c": {
                "count": 2,
                "default": {"number": 0, "sda": 21, "scl": 22, "frequency": 100000}
            },
            "spi": {
                "count": 3,
                "default": {"number": 1, "sck": 18, "mosi": 23, "miso": 19}
            },
            "adc": {"count": 2, "channels": 18},
            "dac": {"count": 2, "channels": 2},
            "pwm": {"count": 16, "frequency_range": "5Hz - 40MHz"}
        },
        "upload": {
            "protocol": "serial",
            "speed": 921600,
            "max_size": 1310720,
            "max_ram": 327680
        }
    },
    
    "esp32s3": {
        "id": "esp32s3",
        "name": "ESP32-S3",
        "manufacturer": "Espressif",
        "platform": "espressif32",
        "framework": "arduino",
        "specs": {
            "flash_size": 8388608,      # 8MB
            "flash_size_mb": 8,
            "ram_size": 1507328,        # 1.5MB
            "ram_size_kb": 1507,
            "cpu": "Dual-core Tensilica Xtensa 32-bit LX7",
            "cpu_frequency": "240MHz"
        },
        "gpio": {
            "total_pins": 49,
            "available_pins": list(range(0, 49)),
            "adc_pins": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            "dac_pins": [],
            "pwm_pins": list(range(0, 49)),
            "spi_pins": [7, 6, 5, 4],
            "i2c_pins": [8, 9],
            "uart_pins": [[44, 43], [17, 18], [20, 19]]
        },
        "peripherals": {
            "uart": {
                "count": 3,
                "default": {"number": 0, "rx": 44, "tx": 43, "baud": 115200}
            },
            "i2c": {
                "count": 1,
                "default": {"number": 0, "sda": 8, "scl": 9, "frequency": 100000}
            },
            "spi": {
                "count": 4,
                "default": {"number": 2, "sck": 6, "mosi": 7, "miso": 5}
            },
            "adc": {"count": 2, "channels": 20},
            "dac": {"count": 0, "channels": 0},
            "pwm": {"count": 16, "frequency_range": "5Hz - 40MHz"}
        },
        "upload": {
            "protocol": "serial",
            "speed": 921600,
            "max_size": 8388608,
            "max_ram": 1507328
        }
    },
    
    "esp32c3": {
        "id": "esp32c3",
        "name": "ESP32-C3",
        "manufacturer": "Espressif",
        "platform": "espressif32",
        "framework": "arduino",
        "specs": {
            "flash_size": 4194304,      # 4MB
            "flash_size_mb": 4,
            "ram_size": 400000,         # 400KB
            "ram_size_kb": 400,
            "cpu": "Single-core RISC-V",
            "cpu_frequency": "160MHz"
        },
        "gpio": {
            "total_pins": 22,
            "available_pins": list(range(0, 22)),
            "adc_pins": [0, 1, 2, 3, 4, 5],
            "dac_pins": [],
            "pwm_pins": list(range(0, 22)),
            "spi_pins": [4, 5, 6, 7],
            "i2c_pins": [8, 9],
            "uart_pins": [[20, 21], [7, 6]]
        },
        "peripherals": {
            "uart": {
                "count": 2,
                "default": {"number": 0, "rx": 20, "tx": 21, "baud": 115200}
            },
            "i2c": {
                "count": 1,
                "default": {"number": 0, "sda": 8, "scl": 9, "frequency": 100000}
            },
            "spi": {
                "count": 2,
                "default": {"number": 2, "sck": 5, "mosi": 6, "miso": 4}
            },
            "adc": {"count": 1, "channels": 6},
            "dac": {"count": 0, "channels": 0},
            "pwm": {"count": 6, "frequency_range": "5Hz - 40MHz"}
        },
        "upload": {
            "protocol": "serial",
            "speed": 460800,
            "max_size": 4194304,
            "max_ram": 400000
        }
    }
}

# ============================================================================
# GPIO PURPOSE MAPPING
# ============================================================================

GPIO_PURPOSES = {
    "led": [2, 4, 5, 13, 14, 15, 25, 26, 27, 32, 33],
    "button": [0, 12, 13, 14, 15, 25, 26, 27, 32, 33],
    "pwm": list(range(0, 40)),
    "adc": [32, 33, 34, 35, 36, 39],
    "i2c": [21, 22],
    "spi": [5, 18, 19, 23],
    "uart": [1, 3, 16, 17],
    "touch": [0, 2, 4, 12, 13, 14, 15, 27, 32, 33],
    "rtc": list(range(0, 40))
}

# ============================================================================
# MCP SERVER SETUP
# ============================================================================

if HAS_MCP:
    server = Server("hardware-database")
else:
    server = None

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

def list_supported_boards():
    """Return list of supported boards."""
    return {
        "boards": list(BOARD_DATABASE.keys()),
        "count": len(BOARD_DATABASE)
    }

def get_board_specs(board_id: str) -> dict:
    """Get complete specifications for a board."""
    if board_id not in BOARD_DATABASE:
        return {"error": f"Board '{board_id}' not found"}
    
    return {"board": board_id, **BOARD_DATABASE[board_id]}

def get_gpio_mapping(board_id: str, purpose: str) -> dict:
    """Get GPIO pins for a specific purpose on a board."""
    if board_id not in BOARD_DATABASE:
        return {"error": f"Board '{board_id}' not found"}
    
    available_pins = GPIO_PURPOSES.get(purpose, [])
    board_pins = BOARD_DATABASE[board_id]["gpio"]["available_pins"]
    
    # Intersection: pins that support this purpose AND exist on board
    compatible_pins = [p for p in available_pins if p in board_pins]
    
    return {
        "board": board_id,
        "purpose": purpose,
        "pins": compatible_pins,
        "count": len(compatible_pins)
    }

def get_peripheral_config(board_id: str, peripheral: str) -> dict:
    """Get default configuration for a peripheral."""
    if board_id not in BOARD_DATABASE:
        return {"error": f"Board '{board_id}' not found"}
    
    board = BOARD_DATABASE[board_id]
    
    if peripheral not in board["peripherals"]:
        return {"error": f"Peripheral '{peripheral}' not supported on {board_id}"}
    
    return {
        "board": board_id,
        "peripheral": peripheral,
        "config": board["peripherals"][peripheral]
    }

# ============================================================================
# MCP TOOL REGISTRATION (if MCP available)
# ============================================================================

if HAS_MCP:
    @server.list_tools()
    async def list_tools():
        """List available tools."""
        return [
            Tool(
                name="list_boards",
                description="List all supported development boards",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_board_specs",
                description="Get hardware specifications for a board",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board": {
                            "type": "string",
                            "description": "Board ID (esp32dev, esp32s3, esp32c3, etc.)"
                        }
                    },
                    "required": ["board"]
                }
            ),
            Tool(
                name="get_gpio_mapping",
                description="Get GPIO pins for a specific purpose",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board": {"type": "string", "description": "Board ID"},
                        "purpose": {
                            "type": "string",
                            "description": "Purpose: led, button, pwm, adc, i2c, spi, uart, etc."
                        }
                    },
                    "required": ["board", "purpose"]
                }
            ),
            Tool(
                name="get_peripheral_config",
                description="Get default configuration for a peripheral (UART, I2C, SPI)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board": {"type": "string"},
                        "peripheral": {
                            "type": "string",
                            "description": "uart, i2c, or spi"
                        }
                    },
                    "required": ["board", "peripheral"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Execute tool calls."""
        
        if name == "list_boards":
            result = list_supported_boards()
        
        elif name == "get_board_specs":
            result = get_board_specs(arguments.get("board", "esp32dev"))
        
        elif name == "get_gpio_mapping":
            result = get_gpio_mapping(
                arguments.get("board", "esp32dev"),
                arguments.get("purpose", "led")
            )
        
        elif name == "get_peripheral_config":
            result = get_peripheral_config(
                arguments.get("board", "esp32dev"),
                arguments.get("peripheral", "uart")
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

# ============================================================================
# STANDALONE MODE (for testing without MCP)
# ============================================================================

async def run_mcp_server():
    """Run the MCP server via stdio."""
    if not HAS_MCP:
        print("❌ MCP SDK not installed. Install with: pip install mcp")
        return
    
    from mcp.server.stdio import stdio_server
    
    print("✓ Hardware Database MCP Server starting...")
    print("  Available boards: " + ", ".join(BOARD_DATABASE.keys()))
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    if HAS_MCP:
        print("\n" + "="*70)
        print("🔧 Hardware Database MCP Server")
        print("="*70)
        asyncio.run(run_mcp_server())
    else:
        # Test mode: Show what the server would return
        print("\n" + "="*70)
        print("🔧 Hardware Database Server (Test Mode - No MCP)")
        print("="*70)
        
        print("\n📋 Supported boards:")
        print(json.dumps(list_supported_boards(), indent=2))
        
        print("\n📊 ESP32-DevKit Specs:")
        print(json.dumps(get_board_specs("esp32dev"), indent=2))
        
        print("\n🔌 LED pins on ESP32-DevKit:")
        print(json.dumps(get_gpio_mapping("esp32dev", "led"), indent=2))
        
        print("\n⚙️ UART config on ESP32-DevKit:")
        print(json.dumps(get_peripheral_config("esp32dev", "uart"), indent=2))
