import os
import json
import requests
from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login

app = Flask(__name__)

# Ruta principal
@app.route('/')
def home():
    return 'Bot de Telegram funcionando!'

# Ruta para el webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update or 'message' not in update:
            return jsonify({'status': 'no message'}), 400

        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if chatbot and text:
            # Respuesta del chatbot
            response = chatbot.chat(text)
            send_message(chat_id, response)

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Función para enviar un mensaje
def send_message(chat_id, text):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    requests.post(send_message_url, json={'chat_id': chat_id, 'text': text})

# Inicialización del chatbot con Hugging Face
try:
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
    else:
        email = os.environ.get("HF_EMAIL")
        password = os.environ.get("HF_PASSWORD")
        sign = Login(email, password)
        cookies = sign.login()
        with open("cookies.json", "w") as f:
            json.dump(cookies.get_dict(), f)

    chatbot = hugchat.ChatBot(cookies=cookies)
except Exception as e:
    print(f"Error al autenticar en Hugging Face: {e}")
    chatbot = None

# Configuración y ejecución del servidor
if __name__ == '__main__':
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    webhook_url = f'{render_url}/webhook'

    # Configurar el webhook
    set_webhook_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}'
    response = requests.get(set_webhook_url)
    print("Webhook response:", response.json())

    # Ejecutar la aplicación
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


