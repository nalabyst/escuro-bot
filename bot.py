import asyncio
from mcstatus import JavaServer
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente (útil para testes locais, no Koyeb as variáveis são injetadas)
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
# ATENÇÃO: Use o ID real do canal onde o bot deve postar.
CANAL_ID = 1430520400575463514 

SERVER_IP = os.getenv("SERVER_IP")
STATUS_ATUAL = None

# Variável global para armazenar o objeto da última mensagem enviada pelo bot
LAST_MESSAGE = None

# Configuração do cliente Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot logado como {client.user}")
    verificar_status.start()

@tasks.loop(minutes=1)
async def verificar_status():
    global STATUS_ATUAL, LAST_MESSAGE
    await client.wait_until_ready()
    
    canal = client.get_channel(CANAL_ID)
    if not canal:
        print(f"ERRO: Canal com ID {CANAL_ID} não encontrado.")
        return
        
    # 1. TENTAR DELETAR A MENSAGEM ANTERIOR (SE EXISTIR)
    if LAST_MESSAGE:
        try:
            await LAST_MESSAGE.delete()
            print("Mensagem anterior deletada com sucesso.")
            LAST_MESSAGE = None 
        except discord.errors.NotFound:
            print("Mensagem anterior não encontrada para deletar (já foi deletada?).")
            LAST_MESSAGE = None
        except Exception as e:
            # Erro de permissão, etc.
            print(f"Erro ao deletar mensagem anterior: {e}")

    # 2. OBTER NOVO STATUS
    try:
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        novo_status = ":green_circle: LIGADO"
    except Exception:
        novo_status = ":red_circle: DESLIGADO"

    # 3. VERIFICAR SE HOUVE MUDANÇA ANTES DE ENVIAR
    if novo_status != STATUS_ATUAL:
        
        # O status MUDOU. Atualizamos a variável de controle e enviamos.
        STATUS_ATUAL = novo_status
        
        # Envia a nova mensagem e ARMAZENA o objeto retornado
        new_message = await canal.send(f"# STATUS: {novo_status}")
        LAST_MESSAGE = new_message # Armazena para ser apagada na próxima rodada

    # Se o status NÃO mudou, o loop termina e não faz nada, 
    # pois a mensagem anterior já foi deletada.
# O client.run(TOKEN) não está aqui, ele é chamado pelo api.py