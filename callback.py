from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from uvicorn.config import LOGGING_CONFIG

from batch.variables import TEST_CHANNEL_ID
from bot.handler.event import get_processed_event
from bot.services.core.post_payload import async_post_message
from bot.utils.signature import verify_signature
from logger import logger


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        yield
    finally:
        logger.info("줍줍이 서버 종료")
        await async_post_message(
            f"줍줍이 종료: {datetime.now().isoformat()}",
            TEST_CHANNEL_ID,
        )


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
    return await get_processed_event(data)


if __name__ == "__main__":
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
        "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    )
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = (
        "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    )
    uvicorn.run("callback:app", host="0.0.0.0", port=5000, workers=4)
