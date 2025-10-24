import os
from flask import Flask
from threading import Thread
import bot 

app = Flask(__name__)

# Variável de controle global (fora das funções)
bot_thread_started = False

def start_bot_thread():
    """Função que roda na thread, iniciando o loop do bot do Discord."""
    global bot_thread_started
    
    if not bot_thread_started:
        print("Iniciando bot do Discord em thread separada...")
        bot_thread_started = True
        
        try:
            # client.run() é o comando que inicia o bot e BLOQUEIA a thread
            bot.client.run(bot.TOKEN)
        except Exception as e:
            print(f"Erro Fatal ao iniciar o bot do Discord: {e}")
            bot_thread_started = False

# INICIA A THREAD DO BOT IMEDIATAMENTE ASSIM QUE O ARQUIVO É CARREGADO PELO GUNICORN
# Este é o ponto mais confiável para iniciar serviços em segundo plano no Gunicorn.
t = Thread(target=start_bot_thread)
t.start()


# Rota para o Health Check do Koyeb
@app.route('/')
def home():
    # Esta rota apenas responde ao Koyeb para manter o Gunicorn ativo
    # O bot já está rodando em sua própria thread (iniciada acima)
    return "Bot Discord Worker está rodando! OK", 200

# O Gunicorn usará esta variável 'app'