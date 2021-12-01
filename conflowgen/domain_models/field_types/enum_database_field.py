"""
These are helper definitions to properly represent enum fields in peewee. The interface is defined by peewee.
"""

import enum


def cast_to_db_value(python_value: enum.Enum):
    """Casts representation in the program to its db representation. It might be None which is handled.
    """
    if python_value is None:
        return None
    return python_value.value
