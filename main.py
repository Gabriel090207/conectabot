from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = FastAPI()

# Carregar variáveis de ambiente
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SEND_TEXT_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
openai.api_key = OPENAI_API_KEY

# Função para enviar mensagem via WhatsApp
async def send_whatsapp(numero, texto):
    payload = {"phone": numero, "message": texto}
    headers = {"client-token": ZAPI_CLIENT_TOKEN}

    async with httpx.AsyncClient() as client:
        await client.post(SEND_TEXT_URL, json=payload, headers=headers)

# ---------------------------
# Definir os Prompts dos atendentes (com base nas opções)
# ---------------------------

PROMPT_MONITORAMENTO = """
Você é um assistente técnico de monitoramento da plataforma.
Seu papel é guiar o usuário para criar um novo monitoramento, responder dúvidas sobre como configurar, e fornecer detalhes do processo.

Quando o usuário diz que não sabe como criar um monitoramento, você deve explicar passo a passo:
1. Como fazer login.
2. Onde acessar a opção de "Novo Monitoramento".
3. O que é necessário preencher (link do diário oficial, id do edital).
4. Explicar que o monitoramento é criado após o preenchimento desses campos.
"""

PROMPT_PLANOS = """
Você é um atendente humano da área de planos.
Seu papel é ajudar o usuário a entender os diferentes planos, suas vantagens e o que está incluso em cada um.
Nunca force uma venda, apenas explique de maneira clara as opções e valores.

Responda de forma natural e simples.
"""

PROMPT_DICAS = """
Você é um assistente do setor de dicas.
Seu papel é ajudar o usuário com dicas sobre como utilizar a plataforma, configurar ferramentas, e obter o melhor desempenho nas ferramentas disponíveis.

Responda de forma amigável, com uma explicação clara e simples.
"""

PROMPT_SUPORTE = """
Você é um atendente humano do suporte.
Seu papel é tirar dúvidas sobre o uso da plataforma, ajudar a solucionar problemas de acesso e fornecer informações de ajuda.

Você deve se comportar de forma amigável, com respostas rápidas e úteis, sem ser robótico.
Sempre que possível, ofereça links úteis para solução de problemas.
"""

# ---------------------------
# Rota para Home
# ---------------------------
@app.get("/")
def home():
    return {"status": "online", "bot": "ConectaBot"}

# ---------------------------
# Webhook Recebendo mensagem
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

    # Menu de opções
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

    # Respostas para cada opção
    if texto == "1":
        await send_whatsapp(numero, "📊 Conectando você ao setor de *Monitoramento*... Aguardando um momento.")
        # Aqui, você pode colocar o nome do bot de monitoramento
        bot_name = "Carlos, seu assistente de Monitoramento"
        await send_whatsapp(numero, f"{bot_name}: Olá! Eu sou o Carlos, seu assistente de Monitoramento. Como posso te ajudar? Se não souber como começar, basta pedir ajuda que explico todo o processo!")
        return {"status": "monitoramento"}

    if texto == "2":
        await send_whatsapp(numero, "💳 Conectando você ao setor de *Planos*... Aguardando um momento.")
        bot_name = "Sofia, especialista em Planos"
        await send_whatsapp(numero, f"{bot_name}: Olá! Eu sou a Sofia, especialista nos planos disponíveis. Como posso te ajudar a escolher o melhor plano para você?")
        return {"status": "planos"}

    if texto == "3":
        await send_whatsapp(numero, "💡 Conectando ao setor de *Dicas*... Aguardando um momento.")
        bot_name = "Lucas, assistente de Dicas"
        await send_whatsapp(numero, f"{bot_name}: Olá! Eu sou o Lucas, e estou aqui para te ajudar com dicas de como aproveitar ao máximo a plataforma. Como posso te ajudar?")
        return {"status": "dicas"}

    if texto == "4":
        await send_whatsapp(numero, "🛠️ Conectando você ao setor de *Suporte*... Aguardando um momento.")
        bot_name = "Mariana, atendente de Suporte"
        await send_whatsapp(numero, f"{bot_name}: Olá! Eu sou a Mariana, atendente de Suporte. Como posso te ajudar? Qualquer dúvida ou problema, estou aqui para ajudar!")
        return {"status": "suporte"}

    if texto == "5":
        await send_whatsapp(numero, "📌 Conectando ao setor de *Outros*... Aguardando um momento.")
        bot_name = "Victor, atendente de Outros"
        await send_whatsapp(numero, f"{bot_name}: Olá! Eu sou o Victor, e estou aqui para ajudar em qualquer outra dúvida ou necessidade. Em que posso te ajudar?")
        return {"status": "outros"}

    # Fallback: caso o bot não reconheça a entrada
    await send_whatsapp(numero, "🤖 Não entendi. Digite *menu* para ver as opções novamente.")
    return {"status": "fallback"}
