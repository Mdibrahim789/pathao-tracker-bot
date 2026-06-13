from fastapi import FastAPI, Request, Response
import os
import requests

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram variables missing")
        return

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/pathao/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("PATHAO WEBHOOK:", data)

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
