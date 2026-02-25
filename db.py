import diskcache
from sqlalchemy import create_engine
import config

_cache = None
_engine = None


def get_cache():
    """Returns the active disk cache. Creates a cache instance if one does not exist.

    Returns:
        diskcache.Cache: The active disk cache
    """
    global _cache
    if _cache is None:
        _cache = diskcache.Cache(config.CACHE_DIR)
    return _cache


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
