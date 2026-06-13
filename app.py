from fastapi import FastAPI, Request, Response
import requests
import os
import json

app = FastAPI()

# =========================
# ENV VARIABLES
# =========================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PATHAO_CLIENT_ID = os.getenv("PATHAO_CLIENT_ID")
PATHAO_CLIENT_SECRET = os.getenv("PATHAO_CLIENT_SECRET")
PATHAO_EMAIL = os.getenv("PATHAO_EMAIL")
PATHAO_PASSWORD = os.getenv("PATHAO_PASSWORD")


# =========================
# TELEGRAM
# =========================

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


# =========================
# PATHAO TOKEN
# =========================

def get_access_token():

    response = requests.post(
        "https://api-hermes.pathao.com/aladdin/api/v1/issue-token",
        json={
            "client_id": PATHAO_CLIENT_ID,
            "client_secret": PATHAO_CLIENT_SECRET,
            "grant_type": "password",
            "username": PATHAO_EMAIL,
            "password": PATHAO_PASSWORD
        },
        timeout=20
    )

    data = response.json()

    return data.get("access_token")


# =========================
# ORDER DETAILS
# =========================

def get_order_info(consignment_id):

    token = get_access_token()

    if not token:
        return None

    response = requests.get(
        f"https://api-hermes.pathao.com/aladdin/api/v1/orders/{consignment_id}/info",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=20
    )

    return response.json()


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {"status": "running"}


# =========================
# TEST TELEGRAM
# =========================

@app.get("/test")
def test():

    send_message("✅ Telegram Test OK")

    return {"success": True}


# =========================
# DEBUG
# =========================

@app.get("/debug")
def debug():

    return {
        "PATHAO_CLIENT_ID": bool(PATHAO_CLIENT_ID),
        "PATHAO_CLIENT_SECRET": bool(PATHAO_CLIENT_SECRET),
        "PATHAO_EMAIL": bool(PATHAO_EMAIL),
        "PATHAO_PASSWORD": bool(PATHAO_PASSWORD),
        "BOT_TOKEN": bool(BOT_TOKEN),
        "CHAT_ID": bool(CHAT_ID)
    }


# =========================
# TOKEN TEST
# =========================

@app.get("/token")
def token():

    return {
        "access_token": get_access_token()
    }


# =========================
# WEBHOOK
# =========================

@app.post("/pathao/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("===================================")
    print(json.dumps(data, indent=2))
    print("===================================")

    event = data.get("event", "Unknown")
    consignment_id = data.get("consignment_id")

    try:

        order_info = get_order_info(consignment_id)

        if order_info and order_info.get("data"):

            order = order_info["data"]

            message = f"""
📦 Pathao Update

🔔 Status: {event}

🆔 Order ID: {order.get('order_id', 'N/A')}
📦 Consignment: {order.get('order_consignment_id', 'N/A')}

👤 Customer: {order.get('recipient_name', 'N/A')}
📞 Phone: {order.get('recipient_phone', 'N/A')}

📍 Address:
{order.get('recipient_address', 'N/A')}

💰 COD Amount: ৳ {order.get('order_amount', 0)}
🚚 Delivery Fee: ৳ {order.get('total_fee', 0)}

🏙 City: {order.get('city_name', '')}
📌 Zone: {order.get('zone_name', '')}

🕒 Created:
{order.get('order_created_at', '')}
"""

            send_message(message)

        else:

            send_message(
                f"📦 Pathao Update\n\n"
                f"Event: {event}\n"
                f"Consignment: {consignment_id}"
            )

    except Exception as e:

        print("ERROR:", str(e))

        send_message(
            f"⚠️ Pathao Error\n\n"
            f"Event: {event}\n"
            f"Consignment: {consignment_id}\n\n"
            f"{str(e)}"
        )

    return Response(
        content="OK",
        status_code=202,
        headers={
            "X-Pathao-Merchant-Webhook-Integration-Secret":
            "f3992ecc-59da-4cbe-a049-a13da2018d51"
        }
    )
