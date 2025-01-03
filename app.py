import os
import requests
from flask import Flask, request
from hugchat import hugchat
from hugchat.login import Login

app = Flask(__name__)

# Ingresar las credenciales de inicio de sesión en huggingface
email = os.environ.get('HF_EMAIL')
password = os.environ.get('HF_PASSWORD')

# Crear una instancia de la clase Login con las credenciales
sign = Login(email, password)

# Iniciar sesión y obtener las cookies
cookies = sign.login()

# Crear una instancia de ChatBot con las cookies de autenticación
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

# Función para enviar mensajes a Telegram
def telegram_bot_sendtext(chat_id, bot_message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={bot_message}'
    response = requests.get(send_text)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Verificar que 'message' esté en los datos
    if 'message' not in data:
        app.logger.warning("Payload no contiene 'message'. Ignorando.")
        return '', 200  # Responder con éxito para evitar reintentos de Telegram

    message_data = data['message']

    # Verificar que el mensaje tenga la estructura necesaria
    if 'chat' not in message_data or 'text' not in message_data:
        app.logger.warning("Mensaje incompleto recibido: %s", message_data)
        return '', 200

    chat_id = message_data['chat']['id']
    user_message = message_data['text']

    # Definir comando de inicio
    START_COMMAND = '/start'

    # Salir del bucle si se recibe un mensaje de despedida
    GOODBYE_MESSAGES = ['salir', 'adios', 'adiós', 'bay', 'chao', 'hasta luego', 'eso es todo', 'adiosito']
    if user_message.lower() in GOODBYE_MESSAGES:
        telegram_bot_sendtext(chat_id, "ChatBot: Hasta luego.")
        return '', 200

    # Verificar si se recibe el comando de inicio
    if user_message.lower() == START_COMMAND:
        # Enviar mensaje de bienvenida
        telegram_bot_sendtext(chat_id, "ChatBot: ¡Hola! Soy un bot diseñado para abordar preguntas en el amplio campo de la salud. Mi especialización me permite proporcionar respuestas precisas y útiles en temas relacionados con la salud o más, no olvides recalcar el idioma en el que hablaremos. ¿En qué puedo ayudarte hoy?")
        return '', 200

    # Obtener la respuesta del chatbot
    try:
        response = chatbot.chat(user_message)  # Método correcto para obtener respuesta
    except Exception as e:
        app.logger.error("Error al obtener respuesta del chatbot: %s", str(e))
        telegram_bot_sendtext(chat_id, "ChatBot: Lo siento, no puedo procesar tu solicitud en este momento.")
        return '', 200

    # Enviar la respuesta del chatbot al usuario de Telegram
    telegram_bot_sendtext(chat_id, f"ChatBot: {response}")

    return '', 200

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


