import functools


def experimental_feature(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if isinstance(result, str):
            return f"실험적인 기능입니다!:\n{result}"
        return result

    return wrapper
