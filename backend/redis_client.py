import redis.asyncio as redis
from config import config

redis_client = redis.Redis(
    host=config.REDIS_HOST, 
    port=config.REDIS_PORT, 
    password=config.REDIS_PASSWORD,
    db=0
)

async def add_key_value_redis(key, value, expire=None):
    await redis_client.set(key, value)
    if expire:
        await redis_client.expire(key, expire)

async def get_value_redis(key):
    return await redis_client.get(key)

async def delete_key_redis(key):
    await redis_client.delete(key)
