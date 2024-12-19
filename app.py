import os
import requests
from flask import Flask, request
from hugchat import hugchat
from hugchat.login import Login

app = Flask(__name__)

# Obtener las credenciales de Hugging Face
email = os.environ.get('HF_EMAIL')
password = os.environ.get('HF_PASSWORD')

# Iniciar sesión y obtener las cookies
try:
    sign = Login(email, password)
    cookies = sign.login()
except Exception as e:
    print(f"Error al autenticar en Hugging Face: {e}")
    cookies = None

# Crear instancia del ChatBot
try:
    if cookies:
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
    else:
        raise ValueError("No se pudo obtener las cookies.")
except Exception as e:
    print(f"Error al inicializar ChatBot: {e}")
    chatbot = None

# Ruta para manejar mensajes de Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if not chatbot:
        return "ChatBot no está disponible.", 500

    data = request.get_json()
    chat_id = data['message']['chat']['id']
    user_message = data['message']['text']

    # Comando de inicio
    START_COMMAND = '/start'
    GOODBYE_MESSAGES = ['salir', 'adios', 'adiós', 'bay', 'chao', 'hasta luego', 'eso es todo', 'adiosito']

    if user_message.lower() in GOODBYE_MESSAGES:
        telegram_bot_sendtext(chat_id, "ChatBot: Hasta luego.")
        return '', 200

    if user_message.lower() == START_COMMAND:
        telegram_bot_sendtext(chat_id, "ChatBot: ¡Hola! Soy un bot diseñado para responder preguntas sobre salud. Indica en qué idioma hablaremos.")
        return '', 200

    # Obtener la respuesta del chatbot
    try:
        response = chatbot.chat(user_message)
        telegram_bot_sendtext(chat_id, f"ChatBot: {response}")
    except Exception as e:
        print(f"Error al obtener respuesta del ChatBot: {e}")
        telegram_bot_sendtext(chat_id, "ChatBot: Lo siento, ocurrió un error. Intenta nuevamente más tarde.")
    
    return '', 200

# Función para enviar mensajes a Telegram
def telegram_bot_sendtext(chat_id, bot_message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={bot_message}'
    response = requests.get(send_text)
    return response.json()

@app.before_request
def setup_webhook():
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    webhook_url = f'{render_url}/webhook'

    set_webhook_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}'
    response = requests.get(set_webhook_url)
    print(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

