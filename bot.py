import asyncio
from mcstatus import JavaServer
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
# ATENÇÃO: Use o ID real do canal onde o bot deve postar.
CANAL_ID = 1430520400575463514 

SERVER_IP = os.getenv("SERVER_IP")

# Variável global para armazenar a última mensagem enviada pelo bot
LAST_MESSAGE = None

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# NOVO: Armazenamento persistente para o status
# Usamos o objeto client, que é persistente e seguro.
client.last_server_status = None 

@client.event
async def on_ready():
    print(f"Bot logado como {client.user}")
    verificar_status.start()

@tasks.loop(minutes=1)
async def verificar_status():
    global LAST_MESSAGE
    await client.wait_until_ready()
    
    canal = client.get_channel(CANAL_ID)
    if not canal:
        print(f"ERRO: Canal com ID {CANAL_ID} não encontrado.")
        return
        
    # 1. OBTER NOVO STATUS (USANDO A LÓGICA CORRETA DE TRY/EXCEPT)
    try:
        server = JavaServer.lookup(SERVER_IP, timeout=5) # Adicionando timeout
        server.status() 
        novo_status = ":green_circle: LIGADO"
    except Exception:
        novo_status = ":red_circle: DESLIGADO"

    # 2. VERIFICAR SE HOUVE MUDANÇA ANTES DE AGIR
    # O status muda quando (novo_status != client.last_server_status)
    if novo_status != client.last_server_status:
        
        # O status MUDOU (ou é a primeira execução).
        
        # 2a. TENTAR DELETAR A MENSAGEM ANTERIOR (SE EXISTIR)
        if LAST_MESSAGE:
            try:
                await LAST_MESSAGE.delete()
                print("Mensagem anterior deletada com sucesso.")
            except discord.errors.NotFound:
                print("Mensagem anterior não encontrada para deletar.")
            except Exception as e:
                print(f"Erro ao deletar mensagem anterior: {e}")
            finally:
                # É crucial limpar a referência após a tentativa, para que não tente apagar denovo se o envio falhar
                LAST_MESSAGE = None
                
        # 2b. ENVIAR A NOVA MENSAGEM
        # ---------------------------
        
        # Atualiza o status armazenado antes de enviar
        client.last_server_status = novo_status 
        
        # Envia a nova mensagem e ARMAZENA o objeto retornado
        new_message = await canal.send(f"# STATUS: {novo_status}")
        LAST_MESSAGE = new_message # Armazena a referência para ser apagada na próxima mudança
    
    # Se o status NÃO mudou, o bot não faz nada.