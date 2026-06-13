from fastapi import FastAPI, Request, Response
import requests
import os
import json

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram config missing")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=10
        )
    except Exception as e:
        print("Telegram Error:", e)


@app.get("/")
def home():
    return {"status": "running"}


@app.get("/test")
def test():
    send_message("✅ Telegram Test OK")
    return {"success": True}


@app.post("/pathao/webhook")
async def webhook(request: Request):

    data = await request.json()

    # Full webhook log
    print("===================================")
    print(json.dumps(data, indent=2))
    print("===================================")

    event = data.get("event", "Unknown")

    send_message(
        f"📦 Pathao Update\n\n"
        f"Event: {event}\n\n"
        f"{data}"
    )

    return Response(
        content="OK",
        status_code=202,
        headers={
            "X-Pathao-Merchant-Webhook-Integration-Secret":
            "f3992ecc-59da-4cbe-a049-a13da2018d51"
        }
    )
