from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

SEND_TEXT_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

@app.get("/")
def home():
    return {"status": "online", "bot": "ConectaBot"}

# ---------------------------
# 📌 Função para enviar msg
# ---------------------------
async def send_whatsapp(numero, texto):
    payload = {"phone": numero, "message": texto}
    headers = {"client-token": ZAPI_CLIENT_TOKEN}

    async with httpx.AsyncClient() as client:
        await client.post(SEND_TEXT_URL, json=payload, headers=headers)

# ---------------------------
# 📌 Webhook Recebendo msg
# ---------------------------
@app.post("/webhook-whatsapp")
async def webhook_whatsapp(request: Request):
    data = await request.json()
    print("📥 RECEBIDO:", data)

    if data.get("fromMe"):
        return {"status": "ignored"}

    numero = data.get("phone")
    texto = data.get("text", {}).get("message")

    if not texto:
        return {"status": "no_text"}

    # Resposta automática simples por enquanto
    await send_whatsapp(numero, "🤖 Recebido! Em breve vou te responder certinho!")
    
    return {"status": "ok", "msg": texto}
