import os
from flask import Flask
from threading import Thread
# Importa o seu bot.py
import bot 

app = Flask(__name__)

# Variável de controle para garantir que o bot inicie apenas uma vez
bot_thread_started = False

# Rota para o Health Check do Koyeb
@app.route('/')
def home():
    global bot_thread_started
    
    # Inicia o bot do Discord APENAS se ainda não tiver sido iniciado
    if not bot_thread_started:
        print("Iniciando bot do Discord em thread separada...")
        t = Thread(target=bot.client.run, args=(bot.TOKEN,))
        t.start()
        bot_thread_started = True
        
    return "Bot Discord Worker está rodando! OK", 200

# O Koyeb usa esta variável 'app' para iniciar o serviço
# O Gunicorn irá executar 'gunicorn api:app'