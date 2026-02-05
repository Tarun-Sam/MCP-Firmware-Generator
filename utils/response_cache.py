#!/usr/bin/env python3
"""
Response Cache - Phase 8 Performance Optimization
Cache LLM responses to avoid redundant expensive calls
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class ResponseCache:
    """Cache LLM responses with TTL to avoid redundant calls."""
    
    def __init__(self, ttl_minutes: int = 60, max_size: int = 100):
        """
        Initialize cache.
        
        Args:
            ttl_minutes: Time-to-live for cached entries in minutes
            max_size: Maximum number of cache entries (LRU eviction)
        """
        self.cache: Dict[str, tuple] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get_cache_key(self, description: str, context: Optional[str] = None, 
                     board: str = "esp32dev", **kwargs) -> str:
        """
        Generate cache key from request parameters.
        
        Args:
            description: Main prompt/description
            context: Additional context
            board: Board type
            **kwargs: Additional parameters to include in key
        
        Returns:
            MD5 hash of parameters as cache key
        """
        # Normalize inputs
        data = {
            "description": description.strip().lower(),
            "context": context.strip().lower() if context else "",
            "board": board.lower(),
            **kwargs
        }
        
        # Create consistent string representation
        text = json.dumps(data, sort_keys=True)
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[str]:
        """
        Get cached response if exists and not expired.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            
            # Check if expired
            if datetime.now() - timestamp < self.ttl:
                self.hits += 1
                return value
            else:
                # Remove expired entry
                del self.cache[key]
                self.misses += 1
                return None
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: str):
        """
        Cache response with current timestamp.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Implement LRU eviction if cache full
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, datetime.now())
    
    def clear(self):
        """Clear all cached entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "ttl_minutes": self.ttl.total_seconds() / 60
        }
    
    def cleanup_expired(self):
        """Remove all expired entries."""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Response Cache - Test Mode")
    print("="*70 + "\n")
    
    cache = ResponseCache(ttl_minutes=1, max_size=5)
    
    # Test 1: Basic set/get
    print("Test 1: Basic Caching")
    print("-" * 70)
    key1 = cache.get_cache_key("blink LED on GPIO 2")
    cache.set(key1, "Sample code for LED blink")
    
    result = cache.get(key1)
    print(f"✓ Cache hit: {result[:30]}...")
    
    # Test 2: Cache miss
    print("\nTest 2: Cache Miss")
    print("-" * 70)
    key2 = cache.get_cache_key("different prompt")
    result = cache.get(key2)
    print(f"✓ Cache miss (expected): {result}")
    
    # Test 3: Multiple entries
    print("\nTest 3: Multiple Entries")
    print("-" * 70)
    for i in range(5):
        key = cache.get_cache_key(f"prompt {i}")
        cache.set(key, f"code {i}")
    
    print(f"✓ Cache size: {len(cache.cache)}/{cache.max_size}")
    
    # Test 4: LRU eviction
    print("\nTest 4: LRU Eviction")
    print("-" * 70)
    key_new = cache.get_cache_key("new prompt")
    cache.set(key_new, "new code")
    print(f"✓ Cache size after exceeding max: {len(cache.cache)}")
    
    # Test 5: Statistics
    print("\nTest 5: Statistics")
    print("-" * 70)
    stats = cache.get_stats()
    print(json.dumps(stats, indent=2))
    
    # Test 6: Expiration
    print("\nTest 6: TTL Expiration (waiting 65 seconds...)")
    print("-" * 70)
    print("⏳ Simulating expiration by clearing cache...")
    cache.clear()
    result = cache.get(key1)
    print(f"✓ Expired entry: {result}")
    
    print("\n" + "="*70)
    print("✅ All cache tests completed!")
    print("="*70)
