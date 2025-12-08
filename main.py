from fastapi import FastAPI, Request
import httpx
import os
import asyncio
from dotenv import load_dotenv

# Carregar as variáveis de ambiente
load_dotenv()

app = FastAPI()

ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

SEND_TEXT_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

@app.get("/")
def home():
    return {"status": "online", "bot": "ConectaBot"}

# Função para enviar a mensagem
async def send_whatsapp(numero, texto):
    payload = {"phone": numero, "message": texto}
    headers = {"client-token": ZAPI_CLIENT_TOKEN}

    async with httpx.AsyncClient() as client:
        await client.post(SEND_TEXT_URL, json=payload, headers=headers)

# Função de webhook para receber mensagens
@app.post("/webhook-whatsapp")
async def webhook_whatsapp(request: Request):
    data = await request.json()
    print("📥 RECEBIDO:", data)

    # Se for uma mensagem enviada pelo próprio bot, ignoramos
    if data.get("fromMe"):
        return {"status": "ignored"}

    numero = data.get("phone")
    
    # Verificar se a chave 'text' existe e se contém uma mensagem
    texto = data.get("text", {}).get("message", "").strip()

    if not texto:
        return {"status": "no_text"}

    # Enviar uma resposta automática (pode ser um tempo de espera simulando um bot)
    await asyncio.sleep(1)  # Simula um pequeno delay antes de enviar a resposta
    await send_whatsapp(numero, "🤖 Recebido! Em breve vou te responder certinho!")

    return {"status": "ok", "msg": texto}
