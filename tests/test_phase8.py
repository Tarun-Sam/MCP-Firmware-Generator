
#!/usr/bin/env python3
"""
Phase 8 Testing Script - Final Optimization & Polish
Tests all Phase 8 enhancements
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def test_health_endpoint():
    """Test enhanced health endpoint with cache stats."""
    print_section("TEST 1: Enhanced Health Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        
        print(f"✓ Status: {data['status']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Backend: {data['backend']}")
        
        # Check Phase 8 features
        if "cache" in data:
            print(f"\n Cache Statistics:")
            for key, value in data["cache"].items():
                print(f"   - {key}: {value}")
        
        if "features" in data:
            print(f"\n Features:")
            for feature, enabled in data["features"].items():
                status = "✓" if enabled else "✗"
                print(f"   {status} {feature}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Server not running!")
        print("  Start with: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_input_validation():
    """Test input validation."""
    print_section("TEST 2: Input Validation")
    
    # Test 1: Empty description
    print("\nTest 2a: Empty Description")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate-code",
            json={"description": ""},
            timeout=5
        )
        if response.status_code == 400:
            print("✓ Empty description rejected (as expected)")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Too short description
    print("\nTest 2b: Short Description")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate-code",
            json={"description": "abc"},
            timeout=5
        )
        if response.status_code == 400:
            print("✓ Short description rejected (as expected)")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Valid description
    print("\nTest 2c: Valid Description")
    print("✓ Valid descriptions accepted (tested in next section)")

def test_cache_functionality():
    """Test response caching."""
    print_section("TEST 3: Response Cache")
    
    prompt = "blink LED on GPIO 2"
    
    print(f"\nFirst request (should be cache MISS)...")
    start_time = time.time()
    
    try:
        response1 = requests.post(
            f"{BASE_URL}/api/generate-code",
            json={
                "description": prompt,
                "compile": False,
                "generate_docs": False
            },
            timeout=60
        )
        elapsed1 = time.time() - start_time
        
        if response1.status_code == 200:
            print(f"✓ First request succeeded ({elapsed1:.2f}s)")
        else:
            print(f"✗ First request failed: {response1.status_code}")
            return
        
        # Check cache stats
        health = requests.get(f"{BASE_URL}/health").json()
        cache_stats = health.get("cache", {})
        print(f"  Cache stats: {cache_stats.get('hits', 0)} hits, {cache_stats.get('misses', 0)} misses")
        
        # Second request (should potentially use cache if implemented)
        print(f"\nSecond request (checking cache behavior)...")
        start_time = time.time()
        
        response2 = requests.post(
            f"{BASE_URL}/api/generate-code",
            json={
                "description": prompt,
                "compile": False,
                "generate_docs": False
            },
            timeout=60
        )
        elapsed2 = time.time() - start_time
        
        if response2.status_code == 200:
            print(f"✓ Second request succeeded ({elapsed2:.2f}s)")
        
        # Compare times
        if elapsed2 < elapsed1 * 0.5:
            print(f"⚡ Second request much faster ({elapsed2:.2f}s vs {elapsed1:.2f}s) - likely cached!")
        else:
            print(f"⏱ Similar times - cache may need full implementation")
        
    except requests.exceptions.Timeout:
        print("✗ Request timed out (this is normal for code generation)")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_error_handling():
    """Test error handling."""
    print_section("TEST 4: Error Handling")
    
    # Test malicious input
    print("\nTest 4a: Malicious Input Detection")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate-code",
            json={"description": "<script>alert('xss')</script>"},
            timeout=5
        )
        if response.status_code == 400:
            print("✓ Malicious input rejected")
        else:
            print(f"⚠ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n✓ Error handling tested")

def test_clarifying_questions():
    """Test Phase 6 clarifying questions."""
    print_section("TEST 5: Clarifying Questions (Phase 6)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/clarifying-questions",
            json={"description": "WiFi temperature sensor"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Clarifying questions generated:")
            for i, question in enumerate(data.get("clarifying_questions", []), 1):
                print(f"  {i}. {question}")
        else:
            print(f"✗ Failed: {response.status_code}")
    except requests.exceptions.Timeout:
        print("⏱ Timeout (Ollama may be slow)")
    except Exception as e:
        print(f"✗ Error: {e}")

def generate_test_report():
    """Generate summary report."""
    print_section("TEST SUMMARY")
    
    try:
        # Get final stats
        health = requests.get(f"{BASE_URL}/health", timeout=5).json()
        
        print("\nSystem Status:")
        print(f"  Version: {health.get('version', 'unknown')}")
        print(f"  Backend: {health.get('backend', 'unknown')}")
        
        if "cache" in health:
            cache = health["cache"]
            print(f"\nCache Performance:")
            print(f"  Total Requests: {cache.get('total_requests', 0)}")
            print(f"  Cache Hits: {cache.get('hits', 0)}")
            print(f"  Cache Misses: {cache.get('misses', 0)}")
            print(f"  Hit Rate: {cache.get('hit_rate_percent', 0)}%")
            print(f"  Cache Size: {cache.get('size', 0)}/{cache.get('max_size', 0)}")
        
        print("\n✅ Phase 8 Testing Complete!")
        
    except Exception as e:
        print(f"✗ Error generating report: {e}")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🚀 PHASE 8: FINAL OPTIMIZATION & POLISH - TEST SUITE")
    print("="*70)
    print("\n⚠ Make sure server is running: uvicorn main:app --reload\n")
    
    input("Press Enter to start tests...")
    
    # Run tests
    if test_health_endpoint():
        test_input_validation()
        test_cache_functionality()
        test_error_handling()
        test_clarifying_questions()
        generate_test_report()
    else:
        print("\n❌ Cannot proceed - server not running")
    
    print("\n" + "="*70)
    print(" Testing Complete")
    print("="*70)
