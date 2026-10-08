from redis.asyncio import Redis
from redis.exceptions import ConnectionError,TimeoutError
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from ..config import settings





async def get_redis_client():
    redis_client=Redis.from_url(
        settings.redis_url,
        max_connections=10,
        decode_response=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
        retry=Retry(ExponentialBackoff(cap=5, base=0.2), retries=3),
        retry_on_error=[ConnectionError, TimeoutError],


    )

    return redis_client