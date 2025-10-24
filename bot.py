import asyncio
from mcstatus import JavaServer
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

# --- ADICIONE ESTAS DUAS LINHAS PARA O SERVIDOR WEB ---
from flask import Flask
from threading import Thread
# ----------------------------------------------------

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
# CANAL_ID deve ser um número inteiro, não uma string.
# Se estiver no .env, você pode fazer: int(os.getenv("CANAL_ID"))
CANAL_ID = 1430520400575463514  # ID do canal onde quer postar

SERVER_IP = os.getenv("SERVER_IP")
STATUS_ATUAL = None

intents = discord.Intents.default()
# O discord.Client é a forma mais simples, mas pode ser discord.ext.commands.Bot dependendo do seu caso.
client = discord.Client(intents=intents)

# --- CÓDIGO DO FLASK (SERVIDOR WEB) ---
# O Koyeb define a porta a ser usada em uma variável de ambiente chamada PORT
app = Flask(__name__)
# O health check do Koyeb vai acessar esta rota
@app.route('/')
def home():
    return "Bot Discord (Worker) está rodando! OK", 200

def run_server():
    # Roda o servidor web em um thread separado
    # host='0.0.0.0' é necessário para que seja acessível externamente
    # A porta é lida da variável de ambiente PORT (que o Koyeb define)
    app.run(host='0.0.0.0', port=os.getenv('PORT'))

def keep_alive():
    # Inicia o servidor web
    t = Thread(target=run_server)
    t.start()
# -----------------------------------------

@client.event
async def on_ready():
    print(f"Bot logado como {client.user}")
    verificar_status.start()

@tasks.loop(minutes=1)
async def verificar_status():
    global STATUS_ATUAL
    # Certifique-se de que o canal é obtido APÓS o bot estar pronto
    # O get_channel pode retornar None se o cache ainda não estiver pronto
    await client.wait_until_ready()
    canal = client.get_channel(CANAL_ID)
    if not canal:
        print(f"ERRO: Canal com ID {CANAL_ID} não encontrado.")
        return

    try:
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        novo_status = ":green_circle: LIGADO"
    except Exception: # Captura qualquer erro, como timeout ou DNS
        novo_status = ":red_circle: DESLIGADO"

    if novo_status != STATUS_ATUAL:
        STATUS_ATUAL = novo_status
        await canal.send(f"# STATUS: {novo_status}")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    # Inicia o servidor HTTP em segundo plano
    keep_alive()
    # Inicia o bot do Discord na thread principal
    client.run(TOKEN)