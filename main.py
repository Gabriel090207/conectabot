from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv
import re
from openai import OpenAI

load_dotenv()

app = FastAPI()

# CREDENCIAIS
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SEND_TEXT_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"

client = OpenAI(api_key=OPENAI_API_KEY)


# ==========================================================
# 📌 ENVIAR WHATSAPP
# ==========================================================
async def send_whatsapp(numero, texto):
    payload = {"phone": numero, "message": texto}
    headers = {"client-token": ZAPI_CLIENT_TOKEN}

    async with httpx.AsyncClient() as client_http:
        await client_http.post(SEND_TEXT_URL, json=payload, headers=headers)


# ==========================================================
# 📌 BASE DE CONHECIMENTO
# ==========================================================
SUPORTE_BASE = """
📌 BASE INTERNA DO SUPORTE CONECTA EDITAL

RADAR:
- Notifica quando o ID aparece no PDF.

PESSOAL:
- Exige ID + NOME completo no PDF.
- Se só ID aparece → não notifica (correto).

HASH:
- Se não houve alteração no PDF → não dispara notificação.

NOTIFICAÇÕES:
- Essencial = Email
- Premium = Email + WhatsApp

HORÁRIOS:
- 05:45 e 23:45

FALHAS COMUNS:
- Nome não consta no PDF → pessoal não notifica
- PDF igual ao anterior → sem alerta

WHATSAPP:
- Só premium recebe.

EMAIL:
- Todos os planos.

PDF QUE NÃO ABRE DIRETO:
- Alguns diários têm link interno do PDF → normal.

REGRA DO SUPORTE:
- Resposta sempre curta, direta e humana.
"""


# ==========================================================
# 📌 IA HUMANIZADA
# ==========================================================
async def gerar_resposta(texto_usuario, personagem):
    prompt = f"""
Você é {personagem}, atendente humano do suporte Conecta Edital.

REGRAS:
- Responda curto, gentil e claro.
- Nunca dê textão.
- Não vender nada.
- Não criar monitoramento.
- Só tirar a dúvida.
- Se não for claro, peça detalhe.

BASE CONHECIMENTO:
{SUPORTE_BASE}

Usuário perguntou:
{texto_usuario}

Resposta:
"""

    resposta = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    return resposta.choices[0].message.content.strip()


# ==========================================================
# 📌 HOME
# ==========================================================
@app.get("/")
def home():
    return {"status": "online", "bot": "Suporte Conecta"}


# ==========================================================
# 📌 WEBHOOK WHATSAPP
# ==========================================================
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

    # ======================================================
    # 👋 SAUDAÇÃO INICIAL COM MENU (SEM TEXTÃO)
    # ======================================================
    if re.match(r"^(oi|olá|bom dia|boa tarde|boa noite|e ai|fala|hey|salve|menu).*$", texto, re.IGNORECASE):
        menu = (
            "Olá 👋 Tudo bem?\n\n"
            "Escolha com quem deseja falar:\n\n"
            "1️⃣ Ana - Monitoramento\n"
            "2️⃣ Carlos - Planos\n"
            "3️⃣ Letícia - Dicas\n"
            "4️⃣ Rafael - Suporte Técnico\n\n"
            "Digite o número:"
        )
        await send_whatsapp(numero, menu)
        return {"status": "menu_inicial"}

    # ======================================================
    # 🤖 ATENDENTES ENTRAM (PERSONAS)
    # ======================================================
    personagens = {
        "1": "Ana, especialista em monitoramento",
        "2": "Carlos, especialista em planos",
        "3": "Letícia, especialista em dicas e orientações",
        "4": "Rafael, suporte técnico"
    }

    if texto in personagens:
        await send_whatsapp(numero, f"Olá! Eu sou {personagens[texto].split(',')[0]} 😊\nComo posso te ajudar?")
        return {"status": f"personagem_{texto}"}

    # ======================================================
    # 🧠 SE NÃO ESCOLHE PERSONAGEM → IA RESPONDE CURTO
    # ======================================================
    # A IA assume e responde como o último personagem chamado (fallback geral)
    resposta = await gerar_resposta(texto, "atendente do suporte")
    await send_whatsapp(numero, resposta)
    return {"status": "ia_respondeu"}
