from config_redis import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
import redis

# Redis connection
rc = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)