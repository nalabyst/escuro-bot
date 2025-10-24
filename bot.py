import asyncio
from mcstatus import JavaServer
import discord
from discord.ext import tasks
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CANAL_ID = 1430520400575463514  # ID do canal onde quer postar

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
    canal = client.get_channel(CANAL_ID)
    try:
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        novo_status = ":green_circle: LIGADO"
    except:
        novo_status = ":red_circle: DESLIGADO"

    if novo_status != STATUS_ATUAL:
        STATUS_ATUAL = novo_status
        await canal.send(f"STATUS: {novo_status}")

client.run(TOKEN)