from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
from slack_bot import get_handler
import os

router = APIRouter()
slack_handler = get_handler()
logger = logging.getLogger(__name__)

@router.post("/slack/events")
async def slack_events(request: Request):
    try:
        if os.getenv("ENV") == "development":
            logger.debug("Dev mode: dumping request body and headers")
            logger.debug(f"Headers: {dict(request.headers)}")
            logger.debug(f"Body: {await request.body()}")

        response = await slack_handler.handle(request)
        logger.debug(f"Slack handler responded with: {response.status_code if hasattr(response, 'status_code') else 'no status'}")
        return response

    except Exception as e:
        logger.exception("Slack event handler error")
        return JSONResponse(status_code=401, content={"error": "invalid request"})




