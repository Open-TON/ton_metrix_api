def rate_limiter(limit: int = 1):
    def decorator_function(func):
        import time

        last_request_time = 0

        def wrapper(*args, **kwargs):
            nonlocal last_request_time

            interval = 1.1 / limit
            current_time = time.time()
            time_since_last_request = current_time - last_request_time
            if time_since_last_request < interval:
                time.sleep(interval - time_since_last_request)
            last_request_time = time.time()
            return func(*args, **kwargs)

        return wrapper

    return decorator_function
