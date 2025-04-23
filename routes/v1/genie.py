from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os
import logging
from slack_bot import async_genie_query

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def home():
    return HTMLResponse("""
    <html>
        <head><title>Databricks Genie Slack Bot</title></head>
        <body>
            <h1>Databricks Genie Slack Bot</h1>
            <p>The bot is running. Slack events are handled via HTTP Mode.</p>
        </body>
    </html>
    """)

class GenieQueryRequest(BaseModel):
    question: str = "What is the most expensive SKU on Databricks?"
    user_id: Optional[str] = "api_user"
    thread_ts: Optional[str] = None

@router.post("/genie")
async def genie_api_query(payload: GenieQueryRequest):
    try:
        result = await async_genie_query(
            user_id=payload.user_id,
            question=payload.question,
            thread_ts=payload.thread_ts
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception("Error during API-based Genie query")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/debug")
async def debug():
    return JSONResponse(content={
        "slack_bot_token": bool(os.environ.get("SLACK_BOT_TOKEN")),
        "slack_channel_id": bool(os.environ.get("SLACK_CHANNEL_ID")),
        "slack_signing_secret": bool(os.environ.get("SLACK_SIGNING_SECRET")),
        "databricks_host": os.environ.get("DATABRICKS_HOST"),
        "databricks_token": bool(os.environ.get("DATABRICKS_TOKEN")),
        "space_id": bool(os.environ.get("SPACE_ID"))
    })

@router.get("/test-logging")
async def test_logging():
    logger.info("Testing logs from /test-logging route")
    return {"status": "Logging test complete"}
