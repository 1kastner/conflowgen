# Decorator class for preview and analysis result caching

class DataSummariesCache:
    cached_results = {}

    # Decorator function to accept function as argument, and return cached result if available or compute and cache
    # result
    @classmethod
    def cache_result(cls, func):
        def wrapper(*args, **kwargs):
            # Create key from function id, name and arguments
            key = str(id(func)) + str(args) + str(kwargs)

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
        cls.cached_results = {}
