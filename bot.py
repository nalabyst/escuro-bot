import asyncio
from mcstatus import JavaServer
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CANAL_ID = 1430520400575463514 

SERVER_IP = os.getenv("SERVER_IP")
STATUS_ATUAL = None

# NOVO: Variável global para armazenar a última mensagem enviada pelo bot
LAST_MESSAGE = None

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot logado como {client.user}")
    verificar_status.start()

@tasks.loop(minutes=1)
async def verificar_status():
    global STATUS_ATUAL, LAST_MESSAGE # Inclua LAST_MESSAGE
    await client.wait_until_ready()
    
    canal = client.get_channel(CANAL_ID)
    if not canal:
        print(f"ERRO: Canal com ID {CANAL_ID} não encontrado.")
        return
        
    # -----------------------------------------------
    # PASSO 1: TENTAR DELETAR A MENSAGEM ANTERIOR
    # -----------------------------------------------
    if LAST_MESSAGE:
        try:
            # O .delete() pode ser usado diretamente no objeto Message
            await LAST_MESSAGE.delete()
            print("Mensagem anterior deletada com sucesso.")
            LAST_MESSAGE = None # Limpa a variável após deletar
        except discord.errors.NotFound:
            # Se a mensagem já tiver sido deletada manualmente
            print("Mensagem anterior não encontrada para deletar (já foi deletada?).")
            LAST_MESSAGE = None
        except Exception as e:
            # Qualquer outro erro de permissão ou API
            print(f"Erro ao deletar mensagem anterior: {e}")

    # -----------------------------------------------
    # PASSO 2: OBTER NOVO STATUS
    # -----------------------------------------------
    try:
        server = JavaServer.lookup(SERVER_IP)
        status = server.status()
        novo_status = ":green_circle: LIGADO"
    except Exception:
        novo_status = ":red_circle: DESLIGADO"

    if novo_status != STATUS_ATUAL:
        STATUS_ATUAL = novo_status
        
        # -----------------------------------------------
        # PASSO 3: ENVIAR NOVA MENSAGEM E ARMAZENAR
        # -----------------------------------------------
        # O método .send() retorna o objeto Message que acabamos de enviar
        new_message = await canal.send(f"# STATUS: {novo_status}")
        LAST_MESSAGE = new_message # Armazena o objeto para a próxima rodada
    else:
        # Se o status não mudou, pode ser que você queira deletar a mensagem antiga
        # mesmo assim e não fazer nada, ou simplesmente não fazer nada.
        # Aqui, vamos apenas manter o loop, sem nova mensagem.
        pass

# ... restante do código ...