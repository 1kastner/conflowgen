import random

from peewee import SqliteDatabase

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.base_model import database_proxy
from conflowgen.tools import get_convert_to_random_value


def setup_sqlite_in_memory_db() -> SqliteDatabase:
    """Set up a database in memory so that all unit tests can run without side effects."""
    sqlite_db = SqliteDatabase(
        ':memory:',
        pragmas={
            'foreign_keys': 1,  # Enforce foreign-key constraints
        })
    database_proxy.initialize(sqlite_db)
    sqlite_db.connect()
    random_bits = random.getrandbits(100)
    sqlite_db.func('assign_random_value')(get_convert_to_random_value(random_bits))
    DataSummariesCache.reset_cache()
    return sqlite_db
