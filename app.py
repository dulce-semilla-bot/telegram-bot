import os
import requests
from flask import Flask, request
from hugchat import hugchat
from hugchat.login import Login

app = Flask(__name__)

# Configurar credenciales y sesión para Hugging Face
email = os.getenv('HF_EMAIL')
password = os.getenv('HF_PASSWORD')
sign = Login(email, password)
cookies = sign.login()
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

# Función para enviar mensajes a Telegram
def send_message(chat_id, text):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=payload)

# Ruta principal del webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    chat_id = data['message']['chat']['id']
    user_message = data['message']['text'].lower()

    if user_message == '/start':
        send_message(chat_id, "Hola, soy un bot de salud. ¿Cómo puedo ayudarte?")
        return '', 200

    if user_message in ['salir', 'adios', 'chao']:
        send_message(chat_id, "Hasta luego.")
        return '', 200

    response = chatbot.chat(user_message)
    send_message(chat_id, response)
    return '', 200

# Configurar webhook en Render al iniciar
@app.before_first_request
def setup_webhook():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    render_url = os.getenv('RENDER_EXTERNAL_URL')  # Render define automáticamente esta variable de entorno
    webhook_url = f'{render_url}/webhook'

    set_webhook_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}'
    response = requests.get(set_webhook_url)
    print(response.json())  # Opcional: Ver la respuesta para depuración

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

