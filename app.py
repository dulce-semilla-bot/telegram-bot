from flask import Flask, request
from hugchat import hugchat
from hugchat.login import Login
import os
import requests

app = Flask(__name__)

# Autenticación en Hugging Face
email = os.environ.get('HF_EMAIL')
password = os.environ.get('HF_PASSWORD')
sign = Login(email, password)
cookies = sign.login()
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

# Webhook para Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' not in data:
        return '', 200

    chat_id = data['message']['chat']['id']
    user_message = data['message']['text']

    response = chatbot.chat(user_message)
    send_telegram_message(chat_id, response)

    return '', 200

def send_telegram_message(chat_id, message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    requests.post(url, json=payload)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



