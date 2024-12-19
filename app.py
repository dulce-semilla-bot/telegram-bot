import os
import requests
from flask import Flask, request
from hugchat.login import Login
from hugchat import hugchat

app = Flask(__name__)

# Autenticación en Hugging Face
try:
    email = os.environ.get("HF_EMAIL")
    password = os.environ.get("HF_PASSWORD")
    sign = Login(email, password)
    cookies = sign.login()
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
except Exception as e:
    print(f"Error al autenticar en Hugging Face: {e}")
    import traceback
    traceback.print_exc()
    chatbot = None

# Ruta para manejar mensajes de Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if not chatbot:
            raise RuntimeError("ChatBot no está disponible.")

        data = request.get_json()
        chat_id = data['message']['chat']['id']
        user_message = data['message']['text']

        START_COMMAND = '/start'
        GOODBYE_MESSAGES = ['salir', 'adios', 'adiós', 'bay', 'chao', 'hasta luego', 'eso es todo', 'adiosito']

        if user_message.lower() in GOODBYE_MESSAGES:
            telegram_bot_sendtext(chat_id, "ChatBot: Hasta luego.")
            return '', 200

        if user_message.lower() == START_COMMAND:
            telegram_bot_sendtext(chat_id, "ChatBot: ¡Hola! Soy un bot diseñado para responder preguntas sobre salud.")
            return '', 200

        response = chatbot.chat(user_message)
        telegram_bot_sendtext(chat_id, f"ChatBot: {response}")
        return '', 200
    except Exception as e:
        print(f"Error al procesar webhook: {e}")
        import traceback
        traceback.print_exc()
        return "Error interno del servidor", 500

# Función para enviar mensajes a Telegram
def telegram_bot_sendtext(chat_id, bot_message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={bot_message}'
    response = requests.get(send_text)
    return response.json()

# Configurar webhook al iniciar
@app.before_first_request
def setup_webhook():
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    webhook_url = f'{render_url}/webhook'

    set_webhook_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}'
    response = requests.get(set_webhook_url)
    print(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

