from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Carregar variáveis de ambiente
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

SEND_TEXT_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

@app.get("/")
def home():
    return {"status": "online", "bot": "ConectaBot"}

# ---------------------------
# 📌 Função para enviar mensagem
# ---------------------------
async def send_whatsapp(numero, texto):
    payload = {"phone": numero, "message": texto}
    headers = {"client-token": ZAPI_CLIENT_TOKEN}

    async with httpx.AsyncClient() as client:
        await client.post(SEND_TEXT_URL, json=payload, headers=headers)

# ---------------------------
# 📌 Webhook Recebendo mensagem
# ---------------------------
@app.post("/api/webhook-whatsapp")
async def webhook_whatsapp(request: Request):
    data = await request.json()
    print("📥 RECEBIDO:", data)

    if data.get("fromMe"):
        return {"status": "ignored"}

    numero = data.get("phone")
    texto = data.get("text", {}).get("message")

    if not texto:
        return {"status": "no_text"}

    # Lógica do menu: Dependendo da opção, encaminha para diferentes atendentes
    if texto.lower() in ["oi", "olá", "bom dia", "boa tarde", "boa noite"]:
        menu = (
            "🌅 *Bom dia* 👋\n\n"
            "Sou o *Conectinha*, seu assistente virtual 🤖✨\n\n"
            "👇 *Selecione uma opção enviando o número:*\n\n"
            "1️⃣ Monitoramento\n"
            "2️⃣ Planos\n"
            "3️⃣ Dicas\n"
            "4️⃣ Suporte\n"
            "5️⃣ Outros\n\n"
            "📌 Digite *menu* a qualquer momento."
        )
        await send_whatsapp(numero, menu)
        return {"status": "menu_sent"}

    # Exemplo de resposta a uma opção
    if texto == "1":
        await send_whatsapp(numero, "📊 Conectando você ao setor de *Monitoramento*...")
        return {"status": "monitoramento"}

    if texto == "2":
        await send_whatsapp(numero, "💳 Conectando você ao setor de *Planos*...")
        return {"status": "planos"}

    if texto == "3":
        await send_whatsapp(numero, "💡 Conectando ao setor de *Dicas*...")
        return {"status": "dicas"}

    if texto == "4":
        await send_whatsapp(numero, "🛠️ Conectando ao setor de *Suporte*...")
        return {"status": "suporte"}

    if texto == "5":
        await send_whatsapp(numero, "📌 Conectando ao setor de *Outros*...")
        return {"status": "outros"}

    # Fallback: caso o bot não reconheça a entrada
    await send_whatsapp(numero, "🤖 Não entendi. Digite *menu* para ver as opções novamente.")
    return {"status": "fallback"}
