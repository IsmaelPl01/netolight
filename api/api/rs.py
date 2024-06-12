"""This modules provides the default Redis connection."""

import redis.asyncio as redis

import api.config

db = redis.Redis.from_url(
    api.config.get_settings().NL_REDIS_URL, decode_responses=True
)
