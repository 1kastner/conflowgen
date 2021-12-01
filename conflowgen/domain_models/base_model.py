"""
Stores the database connection
"""

from peewee import DatabaseProxy
from peewee import Model

database_proxy = DatabaseProxy()


class BaseModel(Model):
    """A base model that will use our Sqlite database."""

    class Meta:
        database = database_proxy
