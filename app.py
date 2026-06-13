@app.post("/pathao/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("PATHAO WEBHOOK:", data)

    event = data.get("event", "Unknown")

    send_message(f"📦 Pathao Update\n\nEvent: {event}")

    return Response(
        status_code=202,
        headers={
            "X-Pathao-Merchant-Webhook-Integration-Secret":
            "f3992ecc-59da-4cbe-a049-a13da2018d51"
        }
    )
