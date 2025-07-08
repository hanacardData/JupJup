from fastapi_cache import FastAPICache


async def save_message_to_cache(key: str, message: str, expire_seconds: int = 86400):
    backend = FastAPICache.get_backend()
    await backend.set(key, message, expire=expire_seconds)


async def load_message_from_cache(key: str) -> str | None:
    backend = FastAPICache.get_backend()
    return await backend.get(key)
