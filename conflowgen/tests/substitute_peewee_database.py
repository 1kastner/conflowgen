from peewee import SqliteDatabase

from conflowgen.domain_models.base_model import database_proxy


def setup_sqlite_in_memory_db() -> SqliteDatabase:
    """Set up a database in memory so that all unit tests can run without side effects."""
    sqlite_db = SqliteDatabase(
        ':memory:',
        pragmas={
            'foreign_keys': 1,  # Enforce foreign-key constraints
        })
    database_proxy.initialize(sqlite_db)
    sqlite_db.connect()
    return sqlite_db
