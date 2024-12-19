from flask import Flask, jsonify
import hugchat
import requests

# Inicializamos Flask
app = Flask(__name__)

# Variable de control para ejecutar algo solo una vez
has_run = False

# Se crea una instancia de ChatBot de HugChat
def initialize_chatbot():
    global chatbot
    try:
        # Aquí debes autenticarte con Hugging Face (con cookies o login)
        sign = hugchat.login.HuggingFaceLogin()
        cookies = sign.login()
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        print("ChatBot inicializado con éxito.")
    except Exception as e:
        print(f"Error al autenticar en Hugging Face: {str(e)}")

@app.before_request
def before_request():
    global has_run
    if not has_run:
        print("Este código solo se ejecuta una vez antes del primer request.")
        initialize_chatbot()
        has_run = True

@app.route('/')
def index():
    return "¡Hola! El bot está en funcionamiento."

@app.route('/webhook', methods=['POST'])
def webhook():
    # Aquí puedes procesar las peticiones del webhook
    return jsonify({"ok": True, "result": True, "description": "Webhook is already set"})

if __name__ == "__main__":
    # Iniciar la aplicación en el puerto 10000 (definido por Render)
    app.run(host="0.0.0.0", port=10000)


