"""
A collection of tools for which no nicer name has been found yet.
"""
from typing import Callable


def docstring_parameter(*args, **kwargs) -> Callable:
    def decorator(obj: object):
        if not hasattr(obj, "__doc__"):
            return obj
        obj.__doc__ = obj.__doc__.format(*args, **kwargs)
        return obj
    return decorator
