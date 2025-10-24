import os
from flask import Flask
from threading import Thread
import bot 

app = Flask(__name__)

# Variável de controle para garantir que o bot inicie apenas uma vez
bot_thread_started = False

def start_bot_thread():
    """Função que roda na thread, iniciando o loop do bot do Discord."""
    global bot_thread_started
    
    # Inicia o bot do Discord APENAS se ainda não tiver sido iniciado
    if not bot_thread_started:
        print("Iniciando bot do Discord em thread separada...")
        bot_thread_started = True
        
        # O cliente .run() é um comando BLOQUEANTE e deve ser a ÚLTIMA coisa 
        # a ser chamada na thread.
        try:
            bot.client.run(bot.TOKEN)
        except Exception as e:
            # Se a execução falhar (ex: Token inválido), o erro será logado
            print(f"Erro Fatal ao iniciar o bot do Discord: {e}")
            bot_thread_started = False

@app.before_first_request
def initialize_bot():
    """Esta função é chamada uma ÚNICA vez antes da primeira requisição."""
    # Garante que a thread é iniciada antes de qualquer Health Check.
    t = Thread(target=start_bot_thread)
    t.start()
    
# Rota para o Health Check do Koyeb
@app.route('/')
def home():
    # Esta rota apenas responde ao Koyeb para manter o Gunicorn ativo
    return "Bot Discord Worker está rodando! OK", 200

# O Gunicorn usará esta variável 'app'