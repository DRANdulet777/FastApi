import aioredis

redis = None

async def init_redis():
    global redis
    redis = await aioredis.from_url("redis://localhost")

async def get_cached(key: str):
    if redis:
        value = await redis.get(key)
        if value:
            return value.decode("utf-8")
    return None

async def set_cache(key: str, value: str, ttl: int = 30):
    if redis:
        await redis.set(key, value, ex=ttl)

async def delete_cache(key: str):
    if redis:
        await redis.delete(key)
