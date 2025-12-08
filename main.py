from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv
import re

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

    # Regex para detectar saudações, como "oi", "olá", "bom dia", etc.
    saudacoes_regex = r"^(oi|olá|bom dia|boa tarde|boa noite|eai|fala|salve|hello|hi|hey|oiê|alô|tudo bem).*$"
    
    # Verificando se o texto do usuário contém alguma saudação
    if re.match(saudacoes_regex, texto, re.IGNORECASE):
        menu = (
            "🌅 *Bom dia* 👋\n\n"
            "Sou o *Conectinha*, seu assistente virtual 🤖✨\n\n"
            "👇 *Selecione uma opção enviando o número:*\n\n"
            "1️⃣ Monitoramento\n"
            "2️⃣ Planos\n"
            "3️⃣ Dicas\n"
            "4️⃣ Suporte\n\n"
            "📌 Digite *menu* a qualquer momento."
        )
        await send_whatsapp(numero, menu)
        return {"status": "menu_sent"}

    # Respostas de acordo com a opção do menu
    if texto == "1":
        # Bot Ana - Monitoramento
        ANA_MONITORAMENTO_PROMPT = """
Oi, sou a Ana, especialista em **Monitoramento**! 🤖

Aqui, temos dois tipos de monitoramento disponíveis:
1. **Radar**: Monitora todos os PDFs que têm o ID colocado no monitoramento.
2. **Pessoal**: Monitora os PDFs que possuem o ID + nome da pessoa.

**Como criar um monitoramento**:
1. Faça o login no portal.
2. Na aba de "Monitoramentos", clique em "Novo Monitoramento" ou "Criar Primeiro Monitoramento" caso não tenha nenhum.
3. Escolha o tipo de monitoramento (Radar ou Pessoal).
4. Preencha as informações, como o **link do diário oficial** e o **ID do edital**.

Se precisar de ajuda, estou aqui para te guiar! 😄
"""
        await send_whatsapp(numero, ANA_MONITORAMENTO_PROMPT)
        return {"status": "monitoramento"}

    if texto == "2":
        # Bot Carlos - Planos
        CARLOS_PLANOS_PROMPT = """
Oi, sou o Carlos, especialista em **Planos**! 😎

Aqui estão os planos disponíveis:

1. **Plano Essencial**:
   - **Preço**: R$ 15.90/mês
   - **Benefícios**:
     - 3 monitoramentos
     - E-mail instantâneo para atualizações
     - Suporte técnico
     - Dashboard de acompanhamento
     - Histórico de publicações (últimos 30 dias)
   - **Notificação**: Só recebe **notificação por e-mail**.

2. **Plano Premium**:
   - **Preço**: R$ 35.90/mês
   - **Benefícios**:
     - Monitoramentos ilimitados
     - E-mail + WhatsApp para notificações
     - Suporte prioritário
     - Acesso antecipado a novas funcionalidades
     - Análise de IA aprimorada
   - **Notificação**: Recebe **notificação por e-mail** e **WhatsApp**.

**Como assinar o plano**:
- Para assinar, vá para a aba de **Planos** no site e escolha o seu plano. 💳

Se tiver mais alguma dúvida ou quiser assinar, é só me avisar!
"""
        await send_whatsapp(numero, CARLOS_PLANOS_PROMPT)
        return {"status": "planos"}

    if texto == "3":
        # Bot Leticia - Dicas
        LETICIA_DICAS_PROMPT = """
Oi, sou a Letícia, especialista em **Dicas**! 📚

As **dicas** são postadas regularmente no nosso site e podem variar desde dicas de estudos até dicas para otimização de monitoramentos e ferramentas.

Você pode conferir todas as dicas atualizadas [aqui](https://siteconectaedital.netlify.app/).

Se precisar de uma dica específica, é só me chamar e eu te ajudo!
"""
        await send_whatsapp(numero, LETICIA_DICAS_PROMPT)
        return {"status": "dicas"}

    if texto == "4":
        # Bot Rafael - Suporte
        RAFAEL_SUPORTE_PROMPT = """
Oi, sou o Rafael, especialista em **Suporte**! 🛠️

Se você tem algum problema ou dúvida, posso te ajudar a abrir um **ticket de suporte** no nosso site.

Aqui está como fazer:
1. Vá até a aba **Suporte** no site.
2. Clique em **Abrir Novo Chamado**.
3. Escolha uma **categoria** para o seu problema.
4. Dê um **título** para o chamado e descreva **detalhadamente** o problema.
5. Aguarde que um de nossos atendentes irá te responder.

Sempre que precisar, estou por aqui para te ajudar! 😄
"""
        await send_whatsapp(numero, RAFAEL_SUPORTE_PROMPT)
        return {"status": "suporte"}

    # Fallback: caso o bot não reconheça a entrada
    await send_whatsapp(numero, "🤖 Não entendi. Digite *menu* para ver as opções novamente.")
    return {"status": "fallback"}
