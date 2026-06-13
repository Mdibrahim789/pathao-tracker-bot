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


@app.get("/debug")
def debug():
    return {
        "PATHAO_CLIENT_ID": bool(os.getenv("PATHAO_CLIENT_ID")),
        "PATHAO_CLIENT_SECRET": bool(os.getenv("PATHAO_CLIENT_SECRET")),
        "PATHAO_EMAIL": bool(os.getenv("PATHAO_EMAIL")),
        "PATHAO_PASSWORD": bool(os.getenv("PATHAO_PASSWORD"))
    }


@app.get("/token")
def get_token():

    response = requests.post(
        "https://api-hermes.pathao.com/aladdin/api/v1/issue-token",
        json={
            "client_id": os.getenv("PATHAO_CLIENT_ID"),
            "client_secret": os.getenv("PATHAO_CLIENT_SECRET"),
            "grant_type": "password",
            "username": os.getenv("PATHAO_EMAIL"),
            "password": os.getenv("PATHAO_PASSWORD")
        }
    )

    return response.json()


@app.post("/pathao/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("===================================")
    print(json.dumps(data, indent=2))
    print("===================================")

    event = data.get("event", "Unknown")
    consignment_id = data.get("consignment_id")

    try:

        token_response = requests.post(
            "https://api-hermes.pathao.com/aladdin/api/v1/issue-token",
            json={
                "client_id": os.getenv("PATHAO_CLIENT_ID"),
                "client_secret": os.getenv("PATHAO_CLIENT_SECRET"),
                "grant_type": "password",
                "username": os.getenv("PATHAO_EMAIL"),
                "password": os.getenv("PATHAO_PASSWORD")
            },
            timeout=20
        )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if access_token and consignment_id:

            info_response = requests.get(
                f"https://api-hermes.pathao.com/aladdin/api/v1/orders/{consignment_id}/info",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                timeout=20
            )

            order_info = info_response.json()

            send_message(
                f"📦 Pathao Update\n\n"
                f"Event: {event}\n"
                f"Consignment: {consignment_id}\n\n"
                f"{json.dumps(order_info, indent=2)}"
            )

        else:

            send_message(
                f"📦 Pathao Update\n\n"
                f"Event: {event}\n"
                f"Consignment: {consignment_id}\n\n"
                f"❌ Access token not found"
            )

    except Exception as e:

        send_message(
            f"❌ Pathao Error\n\n{str(e)}"
        )

    return Response(
        content="OK",
        status_code=202,
        headers={
            "X-Pathao-Merchant-Webhook-Integration-Secret":
            "f3992ecc-59da-4cbe-a049-a13da2018d51"
        }
    )
