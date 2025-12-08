from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Carregar as variáveis do arquivo .env
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

# Definir o URL da Z-API para enviar as mensagens
SEND_TEXT_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

@app.get("/")
def home():
    return {"status": "online", "bot": "ConectaBot"}

# ---------------------------
# 📌 Função para enviar mensagem
# ---------------------------
async def send_whatsapp(numero, texto):
    # Configuração do payload
    payload = {"phone": numero, "message": texto}
    headers = {"client-token": ZAPI_CLIENT_TOKEN}

    # Envio da mensagem via Z-API
    async with httpx.AsyncClient() as client:
        await client.post(SEND_TEXT_URL, json=payload, headers=headers)

# ---------------------------
# 📌 Webhook Recebendo mensagem
# ---------------------------
@app.post("/api/webhook-whatsapp")
async def webhook_whatsapp(request: Request):
    data = await request.json()
    print("📥 RECEBIDO:", data)

    # Se a mensagem foi enviada pelo próprio bot, ignorar
    if data.get("fromMe"):
        return {"status": "ignored"}

    numero = data.get("phone")
    texto = data.get("text", {}).get("message")

    # Se não houver texto na mensagem, retornar sem fazer nada
    if not texto:
        return {"status": "no_text"}

    # Resposta automática simples
    await send_whatsapp(numero, "🤖 Recebido! Em breve vou te responder certinho!")
    
    return {"status": "ok", "msg": texto}
