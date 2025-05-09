from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from uvicorn.config import LOGGING_CONFIG

from bot.handler.event import process_event
from bot.utils.signature import verify_signature
from logger import logger


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def callback(
    request: Request, x_works_signature: str = Header(None)
) -> JSONResponse:
    """메시지 수신을 위한 메인 엔드포인트입니다."""
    raw_body = await request.body()
    raw_text = raw_body.decode()

    if not x_works_signature or not verify_signature(raw_text, x_works_signature):
        logger.warning("Invalid or missing signature.")
        raise HTTPException(status_code=403, detail="Invalid or missing signature")

    data = await request.json()
    return await process_event(data)


if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
        "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    )
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
        "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    )
    uvicorn.run("callback:app", host="0.0.0.0", port=5000, workers=4)
