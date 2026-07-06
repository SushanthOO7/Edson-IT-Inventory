from redis import Redis
from rq import Queue

from app.config import get_settings

settings = get_settings()
redis_connection = Redis.from_url(settings.redis_url)
queue = Queue("default", connection=redis_connection)
