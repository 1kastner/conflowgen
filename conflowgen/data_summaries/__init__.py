# Decorator class for preview and analysis result caching
from functools import wraps


class DataSummariesCache:
    """
    This class is used to cache the results of the data summaries (analyses and previews). This is useful when the
    same data summary is requested multiple times, e.g., when generating a report. In this case, the data summary
    computation is only performed once and the result is cached. The next time the same data summary is requested, the
    cached result is returned instead of computing the data summary again. This can significantly speed up the report
    generation process.
    To use this class, simply decorate the data summary function with the :meth:`.DataSummariesCache.cache_result`
    decorator.
    The cache is automatically reset when input data changes or a new database is used. This can also be done manually
    by calling :meth:`.DataSummariesCache.reset_cache`.
    """

    cached_results = {}
    _hit_counter = {}  # For internal testing purposes

    # Decorator function to accept function as argument, and return cached result if available or compute and cache
    # result
    @classmethod
    def cache_result(cls, func):
        """
        Decorator function to accept function as argument, and return cached result if available or compute and cache
        result.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create key from function id, name and arguments
            key = str(id(func)) + repr(args) + repr(kwargs)

            # Adjust hit counter
            function_name = func.__name__
            if function_name not in cls._hit_counter:
                cls._hit_counter[function_name] = 0
            cls._hit_counter[function_name] += 1

            # Check if key exists in cache
            if key in cls.cached_results:
                return cls.cached_results[key]

            # If not, compute result
            result = func(*args, **kwargs)

            # Cache new result
            cls.cached_results[key] = result
            return result

        return wrapper

    # Reset cache
    @classmethod
    def reset_cache(cls):
        """
        Resets the cache.
        """
        cls.cached_results = {}
        cls._hit_counter = {}
