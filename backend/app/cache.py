import redis.asyncio as redis
import json
from functools import wraps
from typing import Callable, Any
from dotenv import load_dotenv
import os

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0
)

try:
    redis_client.ping()
except redis.ConnectionError:
    print("Warning: Redis connection failed, caching disabled")

def cache(timeout=60):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs: Any) -> Any:
            cache_key = f"{func.__module__}:{func.__name__}:{json.dumps(kwargs, sort_keys=True)}"
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
                result = await func(*args, **kwargs)
                await redis_client.setex(cache_key, timeout, json.dumps(result))
                return result
            except redis.RedisError as e:
                print(f"Redis error: {e}, falling back to function execution")
                return await func(*args, **kwargs)
        return wrapper
    return decorator