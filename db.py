import redis
from sqlalchemy import create_engine
import config

redis_client = None
_engine = None


def get_redis():
    """Returns the active redis client. Creates a client if one does not exist

    Returns:
        Redis: The active Redis client
    """
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    return redis_client


def get_engine():
    """Returns a singleton Postgres engine which can be reused by Pandas.

    Creates the engine once per worker process and reuses it for all database
    connections. This prevents connection leaks that occur when creating a new
    engine (with its own connection pool) on every database query.

    Returns:
        Engine: Singleton Postgres engine
    """
    global _engine
    if _engine is None:
        _engine = create_engine(config.DB_PG_CONN,
                                pool_size=10,
                                max_overflow=5,
                                pool_timeout=30,
                                pool_recycle=1800,
                                pool_pre_ping=True)
    return _engine
