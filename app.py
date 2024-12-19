import os
from flask import Flask, request, jsonify
import hugchat

# Configurar la aplicación Flask
app = Flask(__name__)

# Usar el puerto proporcionado por Render
port = os.getenv('PORT', 10000)  # Si no se encuentra el puerto, usa 10000 por defecto

@app.route('/')
def index():
    return "¡Aplicación en línea!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json  # Asumiendo que los datos llegan en formato JSON
        # Aquí puedes procesar el webhook como necesites
        return jsonify({"ok": True, "result": True, "description": "Webhook received successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inicialización de Hugging Face con manejo de errores
def initialize_chatbot():
    try:
        cookies = hugchat.login()  # Intentar autenticar
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        return chatbot
    except Exception as e:
        print(f"Error al autenticar en Hugging Face: {str(e)}")
        return None

# Configurar antes de la primera solicitud si es necesario
@app.before_first_request
def before_first_request():
    global chatbot
    chatbot = initialize_chatbot()
    if chatbot:
        print("Chatbot inicializado correctamente.")
    else:
        print("Error al inicializar el chatbot.")

# Ruta de prueba para el chatbot
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.json.get('message')
        if chatbot:
            response = chatbot.chat(user_input)  # Suponiendo que el chatbot tenga este método
            return jsonify({"response": response}), 200
        else:
            return jsonify({"error": "El chatbot no está disponible."}), 500
    return jsonify({"message": "Envía un mensaje para chatear."}), 200

# Ejecutar la aplicación Flask en el puerto correcto
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)


