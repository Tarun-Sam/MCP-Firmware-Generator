# MCP Firmware Generator

## Overview
MCP Firmware Generator is an AI-powered embedded firmware generation system that converts natural language requirements into functional ESP32 firmware. The system integrates Large Language Models (LLMs) with MCP-based analysis servers to generate, analyze, validate, and document embedded code through a unified FastAPI backend and web interface.

This project is designed as a research-grade prototype demonstrating the application of AI-assisted program synthesis in embedded systems.

---

## Architecture
The system follows a modular, multi-stage pipeline:

1. **Natural Language Input**
   - User provides firmware requirements via a web UI.

2. **LLM-Based Code Generation**
   - Ollama-hosted LLMs generate ESP32 firmware code from the prompt.

3. **MCP Analysis Servers**
   - Perform code quality checks
   - Estimate memory usage
   - Detect required libraries
   - Validate firmware structure

4. **FastAPI Orchestration Layer**
   - Coordinates LLM inference and MCP analysis
   - Exposes REST APIs for the frontend

5. **Firmware Output & Documentation**
   - Produces ESP32-ready source code
   - Auto-generates structured documentation

---

## Key Features
- Natural language → ESP32 firmware generation
- Modular MCP-based analysis architecture
- Automated code quality and memory analysis
- Library dependency detection
- Web-based interface for interaction
- Research-friendly and extensible design

---

## Tech Stack
- **Backend:** Python, FastAPI  
- **LLMs:** Ollama (local inference)  
- **Analysis:** MCP-based servers  
- **Embedded Target:** ESP32 (PlatformIO structure)  
- **Frontend:** HTML (static UI)  
- **Testing:** Pytest  

---

## Project Structure

```text
MCP-Firmware-Generator/
├── main.py
├── mcp_client.py
├── models.py
├── config.json
├── requirements.txt
├── FIXES_APPLIED.md
├── esp32_project/
│   └── README.md
├── mcp_servers/
├── static/
│   └── index.html
├── utils/
└── tests/
    ├── test_api_response.py
    └── test_phase8.py
```

