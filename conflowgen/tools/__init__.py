"""
A collection of tools for which no nicer name has been found yet.
"""
from typing import Callable, Any, TypeVar

DecoratedType = TypeVar('DecoratedType')


def docstring_parameter(*args, **kwargs) -> Callable:
    def decorator(func: Callable[..., DecoratedType]) -> Callable[..., DecoratedType]:
        if not hasattr(func, "__doc__"):
            return func
        func.__doc__ = func.__doc__.format(*args, **kwargs)
        return func
    return decorator


def hashable(obj: Any) -> bool:
    try:
        hash(obj)
    except TypeError:
        return False
    return True
