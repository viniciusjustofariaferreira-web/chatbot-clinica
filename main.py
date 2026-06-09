from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Suas credenciais
ZAPI_INSTANCE = "3F46651F7F77E1A80832526F0C5E2E11"
ZAPI_TOKEN = "6221D56E388D5D8317845E87"
TYPEBOT_ID = "cmpy9hkn900000bjcquk5j4sy"

sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    
    if not data:
        return jsonify({"status": "ok"})
    
    phone = data.get("phone", "")
    message = data.get("text", {}).get("message", "")
    
    if not phone or not message:
        return jsonify({"status": "ok"})
    
    # Busca ou cria sessão do Typebot
    if phone not in sessions:
        response = requests.post(
            f"https://typebot.io/api/v1/typebots/{TYPEBOT_ID}/whatsapp/start",
            json={"startParams": {"typebot": TYPEBOT_ID},"message": message}
        )
        result = response.json()
        sessions[phone] = result.get("sessionId")
    else:
        session_id = sessions[phone]
        response = requests.post(
            f"https://typebot.io/api/v1/sessions/{session_id}/continueChat",
            json={"message": message}
        )
        result = response.json()
    
    # Envia respostas pro WhatsApp
    messages = result.get("messages", [])
    for msg in messages:
        if msg.get("type") == "text":
            texto = msg.get("content", {}).get("richText", [{}])[0].get("children", [{}])[0].get("text", "")
            if texto:
                requests.post(
                    f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text",
                    json={"phone": phone, "message": texto}
                )
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
