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

def cache(timeout=60):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs: Any) -> Any:
            cache_key = f"{func.__name__}:{json.dumps(kwargs, sort_keys=True)}"
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator