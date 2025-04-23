import os
import re
import asyncio
import logging
from typing import Dict, List, Any

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import MessageStatus

from config import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, FORMAT_TABLES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Async Slack app
if not SLACK_SIGNING_SECRET or not SLACK_BOT_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET must be set in environment variables")

app = AsyncApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
slack_handler = AsyncSlackRequestHandler(app)

# Databricks Genie Setup
w = WorkspaceClient()
genie = w.genie
space_id = os.environ["SPACE_ID"]

# Conversation tracking
conversation_tracker: Dict[str, str] = {}

async def async_genie_query(user_id: str, question: str, thread_ts: str = None):
    try:
        if thread_ts and thread_ts in conversation_tracker:
            conversation_id = conversation_tracker[thread_ts]
            conv = genie.create_message(space_id=space_id, conversation_id=conversation_id, content=question)
        else:
            conv = genie.start_conversation(space_id=space_id, content=question)
            if thread_ts:
                conversation_tracker[thread_ts] = conv.conversation_id

        await asyncio.sleep(1)

        poll_count = 0
        while poll_count < 25:
            message = genie.get_message(conv.space_id, conv.conversation_id, conv.message_id)
            logger.info(f"Genie message: {message}")
            if message.status == MessageStatus.COMPLETED:
                attachment = message.attachments[0] if message.attachments else None
                logger.info(f"Genie attachment: {attachment}")
                query_result = None
                if attachment and attachment.query:
                    query_result = genie.get_message_query_result(
                        conv.space_id, conv.conversation_id, conv.message_id
                    )

                return {
                    "result": {
                        "text": attachment.text.content if attachment and attachment.text else "",
                        "query_description": attachment.query.description if attachment and attachment.query else "",
                        "columns": [col.name for col in query_result.statement_response.manifest.schema.columns] if query_result else [],
                        "rows": query_result.statement_response.result.data_array if query_result else [],
                        "sql_query": attachment.query.query if attachment and attachment.query else ""
                    }
                }
            elif message.status == MessageStatus.FAILED:
                return {"error": "Genie failed to return a response"}
            poll_count += 1
            await asyncio.sleep(2)

        return {"error": "Timed out waiting for Genie response"}
    except Exception as e:
        return {"error": str(e)}

def format_dataframe_for_slack(data: Dict[str, Any]) -> List[Dict]:
    blocks = []

    if data.get("query_description"):
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{data['query_description']}"}
        })

    if data.get("columns") and data.get("rows") and FORMAT_TABLES:
        try:
            header_row = "| " + " | ".join(data["columns"]) + " |"
            divider_row = "| " + " | ".join(["---"] * len(data["columns"])) + " |"
            data_rows = []
            col_widths = [len(col) for col in data["columns"]]
            for row in data["rows"]:
                formatted_cells = []
                for i, cell in enumerate(row):
                    cell_str = str(cell or "")
                    col_widths[i] = max(col_widths[i], len(cell_str))
                    formatted_cells.append(cell_str)
                data_rows.append(formatted_cells)

            padded_header = "| " + " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(data["columns"])) + " |"
            padded_divider = "| " + " | ".join("-" * col_widths[i] for i in range(len(col_widths))) + " |"
            padded_data_rows = ["| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)) + " |" for row in data_rows]
            markdown_table = padded_header + "\n" + padded_divider + "\n" + "\n".join(padded_data_rows)

            if len(markdown_table) > 2900:
                markdown_table = padded_header + "\n" + padded_divider + "\n" + "\n".join(padded_data_rows[:10])
                markdown_table += f"\n\n_Showing 10 of {len(padded_data_rows)} rows_"

            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"```{markdown_table}```"}
            })
        except Exception as e:
            logger.error(f"Error formatting table: {str(e)}")
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Error formatting table: {str(e)}"}
            })

    if data.get("sql_query"):
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Here’s the SQL I used:\n```sql\n{data['sql_query']}\n```"}
        })

    if data.get("text"):
        blocks.insert(1, {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{data['text']}"}
        })

    if not blocks:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "No results to display."}
        })

    return blocks

@app.event("message")
async def handle_message_events(body, say):
    event = body.get("event", {})
    if event.get("subtype") == "bot_add":
        logger.info(f"Bot added to channel: {event.get('channel')}")
        return
    if event.get("type") == "message" and not event.get("subtype"):
        message = {
            "text": event.get("text", ""),
            "user": event.get("user"),
            "channel": event.get("channel"),
            "ts": event.get("ts"),
            "thread_ts": event.get("thread_ts"),
            "channel_type": event.get("channel_type")
        }

        async def say_wrapper(msg_params):
            if "channel" not in msg_params:
                msg_params["channel"] = message["channel"]
            try:
                return await app.client.chat_postMessage(**msg_params)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                logger.debug(f"Message params: {msg_params}")

        await handle_message(message, say_wrapper)

@app.message(re.compile(".*"))
async def handle_message(message, say):
    logger.info(f"Received Slack message: {message}")
    if message.get("bot_id"):
        return
    text = message.get("text", "").strip()
    user_id = message.get("user", "unknown_user")
    channel_type = message.get("channel_type", "")
    if not text:
        return
    if channel_type not in ("channel", "im", "group"):
        return

    thinking_msg = await say({"text": "Loading...", "thread_ts": message.get("ts")})
    try:
        result = await async_genie_query(user_id, text, thread_ts=message.get("thread_ts") or message.get("ts"))
        if "error" in result:
            await say({"text": f"Error: {result['error']}", "thread_ts": message.get("ts")})
            return
        formatted_result = result.get("result", {})
        blocks = format_dataframe_for_slack(formatted_result)

        await app.client.chat_delete(channel=message["channel"], ts=thinking_msg["ts"])
        await say({"blocks": blocks, "thread_ts": message.get("ts")})
    except Exception as e:
        await say({"text": f"Error: {str(e)}", "thread_ts": message.get("ts")})

@app.event("app_mention")
async def handle_mentions(body, say):
    event = body.get("event", {})
    text = re.sub(r"<@[^>]+>\\s*", "", event.get("text", "").strip())
    if text:
        await handle_message(event, say)

def get_handler() -> AsyncSlackRequestHandler:
    return slack_handler
