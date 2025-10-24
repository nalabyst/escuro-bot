import asyncio
from mcstatus import JavaServer
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

load_dotenv()

# COLOQUE O LOAD_DOTENV AQUI SE ESTIVER USANDO O ARQUIVO .env LOCALMENTE.
# LEMBRE-SE DE USAR VARIÁVEIS DE AMBIENTE DO KOYEB PARA O TOKEN E IP.

TOKEN = os.getenv("DISCORD_TOKEN")
# Altere o ID do canal para o ID real. Exemplo de ID:
CANAL_ID = 1430520400575463514 

SERVER_IP = os.getenv("SERVER_IP")
STATUS_ATUAL = None

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot logado como {client.user}")
    verificar_status.start()

@tasks.loop(minutes=1)
async def verificar_status():
    global STATUS_ATUAL
    await client.wait_until_ready()
    
    canal = client.get_channel(CANAL_ID)
    if not canal:
        print(f"ERRO: Canal com ID {CANAL_ID} não encontrado.")
        return

    try:
        # Tenta obter o status do servidor
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        novo_status = ":green_circle: LIGADO"
    except Exception:
        # Se falhar (timeout, IP errado, servidor offline, etc.)
        novo_status = ":red_circle: DESLIGADO"

    if novo_status != STATUS_ATUAL:
        STATUS_ATUAL = novo_status
        await canal.send(f"# STATUS: {novo_status}")

# REMOVA a linha client.run(TOKEN) daqui! 
# A execução agora é controlada pelo api.py