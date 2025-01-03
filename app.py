import os
import requests
from flask import Flask, request
from hugchat import hugchat
from hugchat.login import Login

app = Flask(__name__)

# Obtener las credenciales de inicio de sesión en Hugging Face
email = os.environ.get('HF_EMAIL')
password = os.environ.get('HF_PASSWORD')

# Crear una instancia de la clase Login con las credenciales
sign = Login(email, password)

# Iniciar sesión y obtener las cookies
cookies = sign.login()

# Crear una instancia de ChatBot con las cookies de autenticación
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

# Ruta para manejar mensajes de Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data or 'message' not in data:
        return '', 200

    chat_id = data['message']['chat']['id']
    user_message = data['message']['text']

    # Comando de inicio
    START_COMMAND = '/start'

    # Mensajes de despedida
    GOODBYE_MESSAGES = ['salir', 'adios', 'adiós', 'bay', 'chao', 'hasta luego', 'eso es todo', 'adiosito']

    # Manejar el comando /start
    if user_message.lower() == START_COMMAND:
        welcome_message = (
            "ChatBot: ¡Hola! Soy un bot diseñado para abordar preguntas en el amplio campo de la salud. "
            "Mi especialización me permite proporcionar respuestas precisas y útiles en temas relacionados con la salud o más. "
            "No olvides recalcar el idioma en el que hablaremos. ¿En qué puedo ayudarte hoy?"
        )
        telegram_bot_sendtext(chat_id, welcome_message)
        return '', 200

    # Manejar mensajes de despedida
    if user_message.lower() in GOODBYE_MESSAGES:
        goodbye_message = "ChatBot: Hasta luego. ¡Espero verte de nuevo pronto! 😊"
        telegram_bot_sendtext(chat_id, goodbye_message)
        return '', 200

    # Obtener la respuesta del chatbot
    try:
        response = chatbot.chat(user_message)
    except Exception as e:
        response = "Lo siento, no puedo procesar tu mensaje en este momento. Por favor, inténtalo más tarde."

    # Enviar la respuesta del chatbot al usuario de Telegram
    telegram_bot_sendtext(chat_id, f"ChatBot: {response}")

    return '', 200

# Función para enviar mensajes a Telegram
def telegram_bot_sendtext(chat_id, bot_message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={bot_message}'
    response = requests.get(send_text)
    return response.json()

# Configurar el webhook al inicio
@app.before_first_request
def setup_webhook():
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    webhook_url = f'{render_url}/webhook'

    set_webhook_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}'
    response = requests.get(set_webhook_url)
    print("Webhook setup response:", response.json())

# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))




