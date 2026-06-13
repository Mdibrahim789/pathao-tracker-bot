:::writing{variant="document" id="41852"}
from fastapi import FastAPI, Request, Response

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/pathao/webhook")
async def webhook(request: Request):

    data = await request.json()
    print("PATHAO WEBHOOK:", data)

    return Response(
        content="OK",
        status_code=202,
        headers={
            "X-Pathao-Merchant-Webhook-Integration-Secret":
            "f3992ecc-59da-4cbe-a049-a13da2018d51"
        }
    )
:::


```text
fix indentation and webhook
