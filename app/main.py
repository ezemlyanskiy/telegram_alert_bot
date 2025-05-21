import logging
from http import HTTPStatus

import httpx
from fastapi import FastAPI, HTTPException, Request

from app.config import DM_USERS, TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_CHAT_ID

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_telegram_message(chat_id: str, message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

@app.post("/alert")
async def receive_alert(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid JSON")

    alerts = data.get("alerts", [])
    if not isinstance(alerts, list):
        logger.warning("Missing or invalid 'alerts' list")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Missing alerts")

    for alert in alerts:
        try:
            status = alert.get("status").lower()
            alert_name = alert["labels"].get("alertname", "No name")
            name = alert["labels"].get("name", "No name")
            summary = alert["annotations"].get("summary", "No summary")

            emoji = "🔴" if status == "firing" else "🟢"
            base_msg = f"{emoji} *{alert_name}* is *{status.upper()}*\n_{summary}_\n*{name}*"

            # Send to group
            await send_telegram_message(TELEGRAM_GROUP_CHAT_ID, base_msg)

            # Send DM if it's "conteinerkilled"
            if alert_name.lower() == "conteinerkilled":
                for user_id in DM_USERS:
                    if user_id.strip():
                        await send_telegram_message(user_id, base_msg)
        except Exception as e:
            logger.error(f"Error processing alert: {e}")

    return {"ok": True}
