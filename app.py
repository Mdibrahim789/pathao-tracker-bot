from fastapi import FastAPI, Request, Response
import requests
import os
import json

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PATHAO_CLIENT_ID = os.getenv("PATHAO_CLIENT_ID")
PATHAO_CLIENT_SECRET = os.getenv("PATHAO_CLIENT_SECRET")
PATHAO_EMAIL = os.getenv("PATHAO_EMAIL")
PATHAO_PASSWORD = os.getenv("PATHAO_PASSWORD")

def send_message(text):
try:
requests.post(
f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
json={
"chat_id": CHAT_ID,
"text": text
},
timeout=15
)
except Exception as e:
print("Telegram Error:", e)

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

```
print("TOKEN RESPONSE:", response.text)

try:
    data = response.json()
    return data.get("access_token")
except:
    return None
```

def get_order_info(consignment_id):

```
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

print("ORDER INFO RESPONSE:")
print(response.text)

try:
    result = response.json()
    return result.get("data")
except:
    return None
```

@app.get("/")
def home():
return {"status": "running"}

@app.get("/test")
def test():
send_message("✅ Telegram Test OK")
return {"success": True}

@app.post("/pathao/webhook")
async def webhook(request: Request):

```
data = await request.json()

print("WEBHOOK DATA:")
print(json.dumps(data, indent=2))

event = data.get("event", "Unknown")
consignment_id = data.get("consignment_id")

info = None

if consignment_id:
    info = get_order_info(consignment_id)

if info:

    message = f"""
```

📦 Pathao Update

🔔 Status: {event}

🆔 Order ID: {info.get('order_id')}
📦 Consignment: {info.get('order_consignment_id')}

👤 Customer: {info.get('recipient_name')}
📞 Phone: {info.get('recipient_phone')}

📍 Address:
{info.get('recipient_address')}

💰 COD Amount: ৳{info.get('order_amount')}
🚚 Delivery Fee: ৳{info.get('delivery_fee')}

🏙️ City: {info.get('city_name')}
📌 Zone: {info.get('zone_name')}

🕒 Created: {info.get('order_created_at')}
"""
else:

```
    message = f"""
```

❌ Pathao Details Fetch Failed

Event: {event}
Consignment: {consignment_id}

Check Railway Logs
"""

```
send_message(message)

return Response(
    content="OK",
    status_code=202,
    headers={
        "X-Pathao-Merchant-Webhook-Integration-Secret":
        "f3992ecc-59da-4cbe-a049-a13da2018d51"
    }
)
```
