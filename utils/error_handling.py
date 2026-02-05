#!/usr/bin/env python3
"""
Error Handling - Phase 8 Optimization
Custom exceptions and retry logic for robust error handling
"""

import time
import logging
from typing import Optional, Callable, Any
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("firmware_generator.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class CodeGenerationException(Exception):
    """Base exception for code generation errors."""
    pass


class OllamaConnectionError(CodeGenerationException):
    """Ollama service connection issue."""
    pass


class CompilationError(CodeGenerationException):
    """Code compilation failed."""
    pass


class ValidationError(CodeGenerationException):
    """Input validation failed."""
    pass


class MCPServerError(CodeGenerationException):
    """MCP server communication error."""
    pass


# ============================================================================
# Retry Logic
# ============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    
    Example:
        @retry_with_backoff(max_retries=3, exceptions=(OllamaConnectionError,))
        def generate_code(prompt):
            # Code that might fail
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}"
                        )
                        raise CodeGenerationException(
                            f"Failed after {max_retries} attempts: {str(e)}"
                        )
            
            return None
        
        return wrapper
    return decorator


# ============================================================================
# Validation Functions
# ============================================================================

def validate_description(description: str, min_length: int = 5, max_length: int = 1000) -> None:
    """
    Validate user input description.
    
    Args:
        description: User prompt/description
        min_length: Minimum required length
        max_length: Maximum allowed length
    
    Raises:
        ValidationError: If validation fails
    """
    if not description:
        raise ValidationError("Description cannot be empty")
    
    description = description.strip()
    
    if len(description) < min_length:
        raise ValidationError(
            f"Description too short (minimum {min_length} characters, got {len(description)})"
        )
    
    if len(description) > max_length:
        raise ValidationError(
            f"Description too long (maximum {max_length} characters, got {len(description)})"
        )
    
    # Check for suspicious patterns
    suspicious_patterns = ["<script>", "javascript:", "eval(", "exec("]
    for pattern in suspicious_patterns:
        if pattern.lower() in description.lower():
            raise ValidationError(f"Invalid characters detected: {pattern}")


def validate_generated_code(code: str, min_length: int = 50) -> None:
    """
    Validate generated code quality.
    
    Args:
        code: Generated code string
        min_length: Minimum expected code length
    
    Raises:
        ValidationError: If code appears invalid
    """
    if not code:
        raise ValidationError("Generated code is empty")
    
    code = code.strip()
    
    if len(code) < min_length:
        raise ValidationError(
            f"Generated code too small (minimum {min_length} characters, got {len(code)})"
        )
    
    # Check for essential C++ elements
    required_elements = ["void setup()", "void loop()"]
    missing = [elem for elem in required_elements if elem not in code]
    
    if missing:
        raise ValidationError(
            f"Generated code missing required elements: {', '.join(missing)}"
        )


# ============================================================================
# Safe Execution Wrapper
# ============================================================================

def safe_execute(func: Callable, *args, default_return=None, **kwargs) -> Any:
    """
    Execute function with exception handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        default_return: Value to return on error
        **kwargs: Keyword arguments
    
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        return default_return


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🛡️ Error Handling - Test Mode")
    print("="*70 + "\n")
    
    # Test 1: Validation
    print("Test 1: Input Validation")
    print("-" * 70)
    
    try:
        validate_description("abc")
        print("✗ Should have failed (too short)")
    except ValidationError as e:
        print(f"✓ Caught validation error: {e}")
    
    try:
        validate_description("This is a valid description")
        print("✓ Valid description passed")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test 2: Retry decorator
    print("\nTest 2: Retry with Backoff")
    print("-" * 70)
    
    attempt_count = 0
    
    @retry_with_backoff(max_retries=3, initial_delay=0.1, exceptions=(ValueError,))
    def flaky_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError(f"Attempt {attempt_count} failed")
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"✓ Function succeeded after retries: {result}")
    except CodeGenerationException as e:
        print(f"✗ Function failed: {e}")
    
    # Test 3: Code validation
    print("\nTest 3: Code Validation")
    print("-" * 70)
    
    valid_code = """
    void setup() {
        Serial.begin(115200);
    }
    
    void loop() {
        Serial.println("Hello");
    }
    """
    
    try:
        validate_generated_code(valid_code)
        print("✓ Valid code passed validation")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    try:
        validate_generated_code("int main() { return 0; }")
        print("✗ Should have failed (missing setup/loop)")
    except ValidationError as e:
        print(f"✓ Caught validation error: {e}")
    
    # Test 4: Safe execution
    print("\nTest 4: Safe Execution")
    print("-" * 70)
    
    def risky_function():
        raise RuntimeError("Something went wrong")
    
    result = safe_execute(risky_function, default_return="Fallback")
    print(f"✓ Safe execution returned: {result}")
    
    print("\n" + "="*70)
    print("✅ All error handling tests completed!")
    print("="*70)
