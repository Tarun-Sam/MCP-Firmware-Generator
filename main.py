#!/usr/bin/env python3
# main.py - ESP32 Firmware AI Generator (SIMPLIFIED VERSION 3.2.0)
# Focus on code generation only - skip problematic library installation

import re
import os
import subprocess
import time
import configparser
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import sys

# Import MCP Client
from mcp_client import MCPClient
from mcp_servers.ollama_sampling_server import OllamaSamplingServer
from mcp_servers.docs_generator_server import DocsGeneratorServer

# Phase 8: Performance & Error Handling
from utils.response_cache import ResponseCache
from utils.error_handling import (
    CodeGenerationException, OllamaConnectionError, ValidationError,
    validate_description, validate_generated_code, retry_with_backoff, logger
)

from models import CodeGenerationResponse

# ---- Windows UTF-8 fix (MANDATORY) ----
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

app = FastAPI(
    title="ESP32 Firmware AI Generator",
    description="Code generation with smart library detection",
    version="3.2.0"
)

if os.path.exists("./static"):
    app.mount("/static", StaticFiles(directory="./static"), name="static")

# Initialize MCP Client
mcp_client = MCPClient()
print("✓ MCP Client initialized")

# Initialize Ollama Sampling Server (Phase 6)
ollama_sampler = OllamaSamplingServer()
print("✓ Ollama Sampling Server initialized")

# Initialize Documentation Generator (Phase 7)
docs_generator = DocsGeneratorServer()
print("✓ Documentation Generator initialized")

# Initialize Response Cache (Phase 8)
response_cache = ResponseCache(ttl_minutes=30, max_size=100)
print("✓ Response Cache initialized (30min TTL, max 100 entries)")

try:
    import ollama
    USING_OLLAMA = True
except ImportError:
    USING_OLLAMA = False

USING_OPENAI = False
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    try:
        from openai import OpenAI
        USING_OPENAI = True
    except ImportError:
        USING_OPENAI = False

PLATFORMIO_PROJECT_PATH = os.getenv("PLATFORMIO_PROJECT_PATH", "./esp32_project")
PLATFORMIO_SRC_PATH = os.path.join(PLATFORMIO_PROJECT_PATH, "src")
PLATFORMIO_INI_PATH = os.path.join(PLATFORMIO_PROJECT_PATH, "platformio.ini")
DOCS_PATH = os.path.join(PLATFORMIO_PROJECT_PATH, "docs")

os.makedirs(PLATFORMIO_SRC_PATH, exist_ok=True)
os.makedirs(DOCS_PATH, exist_ok=True)

LIBRARY_MAPPING = {
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
    "LiquidCrystal_I2C.h": "mathertel/LiquidCrystal_I2C",
    "SSD1306.h": "adafruit/Adafruit-SSD1306",
    "TM1637.h": "avishorp/TM1637",
    "Adafruit_ST7735.h": "adafruit/Adafruit-ST7735-Library",
    "Adafruit_ILI9341.h": "adafruit/Adafruit-ILI9341",
    "GxEPD.h": "ZinggJM/GxEPD",
    "MAX7219.h": "sparkfun/SparkFun-LED-Array-8x8",
    "ws2812b.h": "kitesurfer1404/WS2812FX",
    "NeoPixel.h": "adafruit/Adafruit-NeoPixel",
    "PubSubClient.h": "knolleary/PubSubClient",
    "AsyncTCP.h": "me-no-dev/AsyncTCP",
    "ESPAsyncWebServer.h": "me-no-dev/ESPAsyncWebServer",
    "WiFiManager.h": "tzapu/WiFiManager",
    "BluetoothSerial.h": "builtin",
    "BLEDevice.h": "builtin",
    "LoRa.h": "sandeepmistry/arduino-LoRa",
    "RH_RF95.h": "sparkfun/RadioHead",
    "ArduinoJson.h": "bblanchon/ArduinoJson",
    "LittleFS.h": "builtin",
    "SPIFFS.h": "builtin",
    "SD.h": "builtin",
    "FS.h": "builtin",
    "Servo.h": "builtin",
    "ESP32Servo.h": "madhephaestus/ESP32Servo",
    "AccelStepper.h": "mike-matera/AccelStepper",
    "Motor.h": "builtin",
    "NTPClient.h": "taranais/NTPClient",
    "TimeLib.h": "PaulStoffregen/Time",
    "CAN.h": "sandeepmistry/CAN",
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

class CodeGenerationRequest(BaseModel):
    description: str
    context: Optional[str] = None
    compile: bool = True
    generate_docs: bool = True

if USING_OPENAI:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found")
    openai_client = OpenAI(api_key=openai_api_key)
    LLM_MODEL = "gpt-4o-mini"
    print(f"✓ OpenAI initialized: {LLM_MODEL}")
elif USING_OLLAMA:
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11435")
    try:
        ollama_client = ollama.Client(host=ollama_host)
        LLM_MODEL = os.getenv("OLLAMA_MODEL", "codellama")
        print(f"✓ Ollama initialized: {LLM_MODEL}")
    except Exception as e:
        raise ConnectionError(f"Cannot connect to Ollama at {ollama_host}: {e}")
else:
    raise ImportError("Neither OpenAI nor Ollama available")

def extract_includes_from_code(code: str) -> List[str]:
    """Extract all #include statements from generated code."""
    includes = []
    include_pattern = r'#include\s+[<"]([a-zA-Z0-9_./\-]+\.h)[>"]'
    matches = re.findall(include_pattern, code, re.IGNORECASE)
    
    for match in matches:
        header = match.strip()
        if header and header not in includes:
            includes.append(header)
    
    return includes

def detect_required_libraries(code: str) -> List[tuple]:
    """SMART Library Detection - Extract #include from code."""
    required_libs = []
    
    print("\n" + "="*70)
    print("SMART LIBRARY DETECTION")
    print("="*70)
    
    includes = extract_includes_from_code(code)
    print(f"\n✓ Found {len(includes)} #include statements:")
    for inc in includes:
        print(f"  - {inc}")
    
    if not includes:
        print("\n✓ No external libraries needed")
        return []
    
    print(f"\n--- Library Mapping ---")
    for header in includes:
        if header in LIBRARY_MAPPING:
            lib_name = LIBRARY_MAPPING[header]
            if lib_name == "builtin":
                print(f"  {header}: BUILTIN (Arduino framework) - skip")
                continue
            
            required_libs.append((header, lib_name))
            print(f"  {header}: {lib_name}")
        else:
            print(f"  {header}: NOT MAPPED (custom library)")
    
    print(f"\n✓ Total libraries needed: {len(required_libs)}")
    print("="*70 + "\n")
    
    return required_libs

def generate_installation_guide(libraries: List[tuple]) -> str:
    """Generate manual installation instructions for libraries."""
    if not libraries:
        return ""
    
    guide = """
📚 MANUAL LIBRARY INSTALLATION GUIDE
=====================================

Your code needs the following external libraries.
Install them using the PlatformIO IDE or command line.

METHOD 1: Using PlatformIO CLI (Command Line)
----------------------------------------------
"""
    
    for header, lib_name in libraries:
        guide += f"\n➤ {header}\n"
        guide += f"  Command: pio lib install \"{lib_name}\"\n"
        guide += f"  Or:      pio lib install {lib_name.split('/')[-1]}\n"
    
    guide += """

METHOD 2: Using PlatformIO IDE
-------------------------------
1. Open Home → Libraries
2. Search for library by name
3. Click "Install"
4. Restart Reload

METHOD 3: Manual platformio.ini
-------------------------------
Add to D:\\MCP\\esp32_project\\platformio.ini:

[env:esp32dev]
lib_deps =
"""
    
    for header, lib_name in libraries:
        guide += f"    {lib_name}\n"
    
    guide += """

Then PlatformIO will auto-install when you compile.

⚠️ NOTE:
If you get "UnknownPackageError" on Windows, use the simple name:
  pio lib install DHT-sensor-library
  (instead of: pio lib install adafruit/DHT-sensor-library)
"""
    
    return guide

def make_unique_filename(description: str, ext: str = ".cpp") -> str:
    """Generate unique filename - remove ALL special characters."""
    cleaned = description.strip().lower()
    cleaned = re.sub(r"[^a-z0-9\s_\-]", "", cleaned)
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned.strip("_")
    
    if not cleaned or cleaned == "":
        cleaned = "generated"
    
    if len(cleaned) > 35:
        cleaned = cleaned[:35]
    
    timestamp = int(time.time())
    return f"{cleaned}_{timestamp}{ext}"

def save_code_to_file(code: str, description: str) -> str:
    """Save generated code to file."""
    filename = make_unique_filename(description, ".cpp")
    filepath = os.path.join(PLATFORMIO_SRC_PATH, filename)
    
    with open(filepath, "w") as f:
        f.write(code)
    
    return filepath

def clean_code_output(raw_response: str) -> str:
    """Extract code from LLM response."""
    try:
        blocks = re.findall(r"```(?:cpp|c\+\+|c)?\s*([\s\S]*?)```", raw_response, re.IGNORECASE)
        if blocks:
            code = max(blocks, key=lambda b: len(b.strip()))
            return code.strip()
        return raw_response.strip()
    except Exception:
        return raw_response.strip()

def compile_code() -> dict:
    """Compile code using PlatformIO."""
    try:
        result = subprocess.run(
            ["pio", "run", "-e", "esp32dev"],
            cwd=PLATFORMIO_PROJECT_PATH,
            capture_output=True,
            text=True,
            timeout=180
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "⏱ Compilation timed out", "returncode": -1}
    except FileNotFoundError:
        return {"success": False, "output": "❌ PlatformIO not found", "returncode": -1}
    except Exception as e:
        return {"success": False, "output": f"❌ Error: {str(e)}", "returncode": -1}

def parse_compilation_errors(output: str) -> Dict:
    """Parse compilation errors."""
    errors_dict = {
        "syntax_errors": [],
        "missing_headers": [],
        "undefined_references": [],
        "type_errors": [],
        "other_errors": []
    }
    
    for line in output.split("\n"):
        if "error:" not in line.lower():
            continue
        
        line_clean = line.strip()
        if not line_clean:
            continue
        
        if "fatal error:" in line.lower() and ".h:" in line:
            errors_dict["missing_headers"].append(line_clean)
        elif "undefined reference" in line.lower():
            errors_dict["undefined_references"].append(line_clean)
        elif "error:" in line.lower() and ("expected" in line or "undeclared" in line):
            errors_dict["syntax_errors"].append(line_clean)
        elif "error:" in line.lower() and ("type" in line or "cannot" in line):
            errors_dict["type_errors"].append(line_clean)
        else:
            errors_dict["other_errors"].append(line_clean)
    
    return errors_dict

def generate_troubleshooting_suggestions(error_dict: Dict) -> List[str]:
    """Generate troubleshooting suggestions."""
    suggestions = []
    
    if error_dict["missing_headers"]:
        suggestions.append("📦 Missing libraries - see installation guide above")
    if error_dict["syntax_errors"]:
        suggestions.append("🔧 Syntax errors detected")
    if error_dict["undefined_references"]:
        suggestions.append("🔗 Undefined references - check library installation")
    if error_dict["type_errors"]:
        suggestions.append("⚠ Type errors detected")
    if error_dict["other_errors"]:
        suggestions.append("❓ Other errors detected. Check compilation output.")
    
    if not any([error_dict[k] for k in error_dict]):
        suggestions.append("✓ No compilation errors detected.")
    
    return suggestions

def generate_code_with_llm(description: str, context: Optional[str] = None) -> str:
    """Generate ESP32 code using LLM."""
    
    system_prompt = """You are an expert ESP32 firmware developer.
    
REQUIREMENTS:
1. Generate ONLY complete Arduino sketches
2. Use void setup() and void loop()
3. Do NOT include fake libraries
4. Use Arduino standard functions only
5. For PWM: Use ledcSetup/ledcAttachPin/ledcWrite
6. Use concrete GPIO numbers
7. Include Serial.begin(115200) if needed
8. Return ONLY code in ```cpp``` blocks"""
    
    user_message = f"Generate ESP32 Arduino code for: {description}"
    if context:
        user_message += f"\n\nContext: {context}"
    
    try:
        if USING_OPENAI:
            response = openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.6,
                max_tokens=2048
            )
            return response.choices[0].message.content
        
        elif USING_OLLAMA:
            response = ollama_client.chat(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=False
            )
            return response["message"]["content"]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

def generate_documentation_with_llm(code: str, description: str) -> str:
    """Generate markdown documentation."""
    
    doc_prompt = f"""Generate markdown documentation for this ESP32 code.

Description: {description}

Code:
{code}

Include:
1. Project Overview
2. Hardware Requirements
3. Libraries Used
4. How It Works
5. Pin Configuration
6. Troubleshooting

Return ONLY markdown, no code blocks."""
    
    try:
        if USING_OPENAI:
            response = openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a technical writer."},
                    {"role": "user", "content": doc_prompt}
                ],
                temperature=0.5,
                max_tokens=2048
            )
            return response.choices[0].message.content
        
        elif USING_OLLAMA:
            response = ollama_client.chat(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a technical writer."},
                    {"role": "user", "content": doc_prompt}
                ],
                stream=False
            )
            return response["message"]["content"]
    
    except Exception as e:
        print(f"⚠ Documentation error: {str(e)}")
        return None

def save_documentation(documentation: str, code_filename: str) -> str:
    """Save documentation to file."""
    if not os.path.exists(DOCS_PATH):
        os.makedirs(DOCS_PATH)
    
    base_filename = os.path.splitext(os.path.basename(code_filename))[0]
    doc_filename = f"{base_filename}_README.md"
    doc_path = os.path.join(DOCS_PATH, doc_filename)
    
    try:
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(documentation)
        print(f"✓ Documentation saved")
        return doc_path
    except Exception as e:
        print(f"⚠ Documentation save error: {str(e)}")
        return None

def cleanup_old_files(max_files: int = 3):
    """Remove old generated files."""
    try:
        if not os.path.exists(PLATFORMIO_SRC_PATH):
            return
        
        files = sorted(
            [f for f in os.listdir(PLATFORMIO_SRC_PATH) if f.endswith(".cpp")],
            key=lambda x: os.path.getmtime(os.path.join(PLATFORMIO_SRC_PATH, x)),
            reverse=True
        )
        
        if len(files) > max_files:
            for old_file in files[max_files:]:
                try:
                    os.remove(os.path.join(PLATFORMIO_SRC_PATH, old_file))
                except Exception:
                    pass
    except Exception:
        pass

@app.get("/")
async def root():
    """Serve web UI."""
    return FileResponse("./static/index.html", media_type="text/html")

@app.get("/health")
async def health_check():
    """Health check endpoint with Phase 8 enhancements."""
    pio_installed = os.system("pio --version > /dev/null 2>&1") == 0
    
    # Get cache statistics
    cache_stats = response_cache.get_stats()
    
    return {
        "status": "healthy",
        "backend": "Ollama" if USING_OLLAMA else "OpenAI" if USING_OPENAI else "None",
        "model": LLM_MODEL,
        "platformio_installed": pio_installed,
        "version": "3.2.0-phase8",
        "cache": cache_stats,
        "features": {
            "mcp_client": True,
            "ollama_sampling": True,
            "docs_generator": True,
            "response_cache": True,
            "error_handling": True
        }
    }

@app.post("/api/clarifying-questions")
async def get_clarifying_questions(request: CodeGenerationRequest):
    """Get clarifying questions for better code generation (Phase 6)."""
    try:
        questions = ollama_sampler.generate_clarifying_questions(
            request.description,
            num_questions=3
        )
        return {
            "initial_prompt": request.description,
            "clarifying_questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

@app.post("/api/refine-and-generate")
async def refine_and_generate(
    initial_prompt: str,
    questions_answers: Dict[str, str],
    compile: bool = True,
    generate_docs: bool = True
):
    """Refine requirements and generate improved code (Phase 6)."""
    try:
        # Refine requirements
        print(f"\n{'='*70}")
        print(f"🔮 Refining requirements for: {initial_prompt}")
        print(f"{'='*70}")
        
        refined = ollama_sampler.refine_requirements(
            initial_prompt,
            questions_answers
        )
        print(f"✓ Requirements refined")
        
        # Generate improved prompt
        improved_prompt = ollama_sampler.generate_improved_prompt(
            initial_prompt,
            refined
        )
        print(f"✓ Improved prompt generated")
        
        # Use existing code generation with improved context
        request = CodeGenerationRequest(
            description=initial_prompt,
            context=improved_prompt,
            compile=compile,
            generate_docs=generate_docs
        )
        
        return await generate_code(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@app.post("/api/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate ESP32 firmware code with Phase 8 optimizations."""
    
    # Phase 8: Input validation
    try:
        validate_description(request.description)
    except ValidationError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    # Phase 8: Check cache first
    cache_key = response_cache.get_cache_key(
        description=request.description,
        context=request.context or "",
        compile=request.compile,
        generate_docs=request.generate_docs
    )
    
    cached_response = response_cache.get(cache_key)
    if cached_response:
        logger.info("Using cached response")
        print("\n" + "="*70)
        print("⚡ Cache Hit! Returning cached response")
        print("="*70)
        # Return cached response (would need to deserialize)
        # For now, continue with generation
    
    cleanup_old_files(max_files=2)
    
    print(f"\n{'='*70}")
    print(f"📝 Generating: {request.description}")
    print(f"{'='*70}")
    
    # Phase 8: Code generation with error handling
    try:
        logger.info(f"Starting code generation: {request.description[:50]}...")
        generated = generate_code_with_llm(request.description, request.context)
        code_only = clean_code_output(generated)
        
        # Phase 8: Validate generated code
        validate_generated_code(code_only)
        logger.info("Code generation successful")
        
    except ValidationError as e:
        logger.error(f"Generated code validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Invalid code generated: {str(e)}")
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(status_code=503, detail="Code generation service unavailable")
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")
    
    filepath = save_code_to_file(code_only, request.description)
    print(f"✓ Code saved: {filepath}")
    
    compilation_status = None
    compilation_output = None
    detected_libraries = None
    error_summary = None
    troubleshooting_suggestions = []
    documentation = None
    installation_guide = None
    
    # DETECT LIBRARIES (NO INSTALLATION)
    print(f"\n>>> Smart library detection...")
    detected_libraries = detect_required_libraries(code_only)
    
    if detected_libraries:
        installation_guide = generate_installation_guide(detected_libraries)
        print(f"\n📚 Generated installation guide for {len(detected_libraries)} libraries")
    
    # MCP CLIENT ANALYSIS
    print(f"\n>>> Querying MCP servers for analysis...")
    
    # 1. Hardware specs
    hardware_specs = mcp_client.get_board_specs("esp32dev")
    print(f"✓ Got hardware specs: {hardware_specs['name']}")
    
    # 2. Library analysis
    library_analysis = mcp_client.analyze_libraries(code_only, "esp32dev")
    print(f"✓ Found {library_analysis['external_count']} external libraries")
    
    # 3. Code quality
    quality_analysis = mcp_client.analyze_code_quality(code_only, "esp32dev")
    print(f"✓ Code quality score: {quality_analysis['quality_score']}/100")
    print(f"   Severity: {quality_analysis.get('severity', 'unknown')}")
    
    # COMPILE CODE
    if request.compile:
        print(f"\n🔨 Compiling code...")
        compile_result = compile_code()
        compilation_output = compile_result["output"]
        
        if compile_result["success"]:
            compilation_status = "✓ Compilation successful!"
            print("✓ Compilation successful!")
        else:
            compilation_status = "✗ Compilation failed"
            print("❌ Compilation failed")
        
        if compilation_output:
            error_dict = parse_compilation_errors(compilation_output)
            error_counts = {k: len(v) for k, v in error_dict.items()}
            error_summary = (
                f"Syntax: {error_counts['syntax_errors']}, "
                f"Missing Headers: {error_counts['missing_headers']}, "
                f"Undefined Refs: {error_counts['undefined_references']}, "
                f"Type Errors: {error_counts['type_errors']}, "
                f"Other: {error_counts['other_errors']}"
            )
            troubleshooting_suggestions = generate_troubleshooting_suggestions(error_dict)
    
    # GENERATE DOCUMENTATION (Phase 7: Enhanced) - ALWAYS GENERATE
    if request.generate_docs:
        print(f"\n📚 Generating comprehensive documentation (Phase 7)...")
        try:
            # Use Phase 7 Documentation Generator
            doc_content = docs_generator.generate_full_documentation(
                code=code_only,
                description=request.description,
                libraries=[lib for lib, _ in detected_libraries] if detected_libraries else []
            )
            
            if doc_content:
                doc_path = save_documentation(doc_content, filepath)
                # Return FULL documentation content for frontend display
                documentation = doc_content  # Changed: return full content, not truncated
                print(f"✓ Professional documentation generated ({len(doc_content)} chars)")
                logger.info(f"Documentation generated: {len(doc_content)} characters")
        except Exception as e:
            error_msg = f"Doc generation error: {str(e)}"
            print(f"⚠ {error_msg}")
            logger.error(error_msg)
            # Generate fallback documentation
            documentation = f"# {request.description}\n\nDocumentation generation encountered an error. Please refer to the generated code."
    
    print(f"\n{'='*70}\n")
    
    return CodeGenerationResponse(
        description=request.description,
        generated_code=code_only,
        file_path=filepath,
        compilation_status=compilation_status,
        compilation_output=compilation_output[-2000:] if compilation_output else None,
        detected_libraries=[f"{h} → {l}" for h, l in detected_libraries] if detected_libraries else None,
        error_summary=error_summary,
        troubleshooting_suggestions=troubleshooting_suggestions if troubleshooting_suggestions else None,
        documentation=documentation,
        installation_guide=installation_guide,
        # NEW: MCP Analysis Results
        hardware_info=hardware_specs,
        code_quality_score=quality_analysis['quality_score'],
        memory_usage=quality_analysis.get('estimated_ram_usage_percent'),
        quality_issues=quality_analysis.get('issues', []),  # Now structured!
        quality_warnings=quality_analysis.get('warnings', []) 
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )