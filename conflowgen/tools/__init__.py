"""
A collection of tools for which no nicer name has been found yet.
"""
import hashlib
from typing import Callable, Any, TypeVar

DecoratedType = TypeVar('DecoratedType')  # pylint: disable=invalid-name


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


def get_convert_to_random_value(random_bits):
    def convert_to_random_value(row_id):
        hash = hashlib.new('sha256')
        hash.update((random_bits + row_id).to_bytes(16, 'big'))
        return hash.hexdigest()
    return convert_to_random_value
