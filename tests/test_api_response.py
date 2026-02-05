#!/usr/bin/env python3
"""
API Response Test - Verify all fields are populated correctly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_generate_code_response():
    """Test /api/generate-code endpoint returns complete data."""
    
    print("\n" + "="*70)
    print(" Testing API Response Structure")
    print("="*70 + "\n")
    
    # Test prompt
    prompt = "blink LED on GPIO 2 every second"
    
    print(f"📝 Testing with prompt: '{prompt}'")
    print(f"⏳ This may take 30-60 seconds...\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate-code",
            json={
                "description": prompt,
                "compile": False,  # Skip compilation for faster test
                "generate_docs": True  # Enable documentation
            },
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        
        print("✅ Response received! Checking fields...\n")
        
        # Check required fields
        required_fields = [
            "description",
            "generated_code",
            "file_path",
            "hardware_info",
            "code_quality_score",
            "memory_usage",
            "detected_libraries"
        ]
        
        print("📋 REQUIRED FIELDS:")
        for field in required_fields:
            value = data.get(field)
            if value is not None:
                if isinstance(value, str):
                    preview = value[:50] + "..." if len(value) > 50 else value
                elif isinstance(value, dict):
                    preview = f"{len(value)} keys"
                elif isinstance(value, list):
                    preview = f"{len(value)} items"
                else:
                    preview = str(value)
                print(f"  ✅ {field}: {preview}")
            else:
                print(f"  ❌ {field}: NULL")
        
        # Check documentation
        print("\n📚 DOCUMENTATION:")
        if data.get("documentation"):
            doc_len = len(data["documentation"])
            print(f"  ✅ documentation: {doc_len} characters")
            print(f"  Preview: {data['documentation'][:100]}...")
        else:
            print(f"  ❌ documentation: NULL or empty")
        
        # Check hardware info details
        print("\n🔧 HARDWARE INFO DETAILS:")
        if data.get("hardware_info"):
            hw = data["hardware_info"]
            hw_fields = [
                "name", "flash_mb", "ram_kb", "gpio_pins", 
                "adc_channels", "uart_ports", "i2c_ports", 
                "spi_ports", "pwm_channels"
            ]
            for field in hw_fields:
                value = hw.get(field)
                status = "✅" if value is not None else "❌"
                print(f"  {status} {field}: {value}")
        else:
            print("  ❌ hardware_info is NULL")
        
        # Check libraries
        print("\n📦 DETECTED LIBRARIES:")
        if data.get("detected_libraries"):
            for i, lib in enumerate(data["detected_libraries"][:5], 1):
                print(f"  {i}. {lib}")
            if len(data["detected_libraries"]) > 5:
                print(f"  ... and {len(data['detected_libraries']) - 5} more")
        else:
            print("  ℹ️ No external libraries detected")
        
        # Check quality info
        print("\n📊 QUALITY ANALYSIS:")
        print(f"  Score: {data.get('code_quality_score', 'N/A')}/100")
        print(f"  Memory: {data.get('memory_usage', 'N/A')}%")
        print(f"  Issues: {len(data.get('quality_issues', []))}")
        print(f"  Warnings: {len(data.get('quality_warnings', []))}")
        
        # Validation summary
        print("\n" + "="*70)
        print(" VALIDATION SUMMARY")
        print("="*70)
        
        checks = {
            "Code generated": bool(data.get("generated_code")),
            "Documentation generated": bool(data.get("documentation") and len(data.get("documentation", "")) > 100),
            "Hardware info complete": bool(data.get("hardware_info") and data["hardware_info"].get("name")),
            "Quality score present": data.get("code_quality_score") is not None,
            "Memory usage present": data.get("memory_usage") is not None,
        }
        
        for check, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {check}")
        
        all_passed = all(checks.values())
        print("\n" + "="*70)
        if all_passed:
            print("🎉 ALL CHECKS PASSED! API response is complete.")
        else:
            print("⚠️ SOME CHECKS FAILED. Review the output above.")
        print("="*70 + "\n")
        
        return all_passed
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("   Start server with: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 MCP Firmware Generator - API Response Test")
    print("⚠️  Make sure server is running: uvicorn main:app --reload\n")
    
    input("Press Enter to start test...")
    
    success = test_generate_code_response()
    
    exit(0 if success else 1)
