import redis
from cachetools import LRUCache
import hashlib
import os
from tenacity import retry, stop_after_attempt


class CacheService:
    def __init__(self):
        # Free Tier: In-memory cache
        self.local_cache = LRUCache(maxsize=1024)

        # Paid Tier: Redis Cloud
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=6379,
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        ) if os.getenv("USE_PAID_CACHE") else None

    @retry(stop=stop_after_attempt(3))
    def get(self, key: str, is_premium: bool = False):
        """Hybrid cache retrieval"""
        # Try paid cache first for premium users
        if is_premium and self.redis:
            if value := self.redis.get(key):
                return value

        # Fallback to free local cache
        return self.local_cache.get(key, None)

    @retry(stop=stop_after_attempt(3))
    def set(self, key: str, value: str, ttl: int = 3600, is_premium: bool = False):
        """Hybrid cache storage"""
        # Store in paid cache for premium
        if is_premium and self.redis:
            self.redis.setex(key, ttl, value)

        # Always store in local cache
        self.local_cache[key] = value

    def generate_key(self, *args) -> str:
        """Create consistent cache key"""
        return hashlib.sha256(":".join(str(a) for a in args).encode()).hexdigest()