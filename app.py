@app.get("/test")
def test():
    send_message("✅ Telegram Test OK")
    return {"ok": True}
