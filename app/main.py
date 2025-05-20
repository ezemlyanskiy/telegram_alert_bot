import httpx
from fastapi import FastAPI, Request
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_CHAT_ID, DM_USERS

app = FastAPI()

async def send_telegram_message(chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

@app.post("/alert")
async def receive_alert(request: Request):
    data = await request.json()

    alerts = data.get("alerts", [])
    for alert in alerts:
        status = alert.get("status").lower()
        name = alert["labels"].get("alertname", "No name")
        summary = alert["annotations"].get("summary", "No summary")

        emoji = "🔴" if status == "firing" else "🟢"
        base_msg = f"{emoji} *{name}* is *{status.upper()}*\n_{summary}_"

        # Send to group
        await send_telegram_message(TELEGRAM_GROUP_CHAT_ID, base_msg)

        # Send DM if it's "conteinerkilled"
        if name.lower() == "conteinerkilled":
            for user_id in DM_USERS:
                if user_id.strip():
                    await send_telegram_message(user_id, base_msg)

    return {"ok": True}
