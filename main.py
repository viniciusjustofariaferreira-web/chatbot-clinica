from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ZAPI_INSTANCE = "3F46651F7F77E1A80832526F0C5E2E11"
ZAPI_TOKEN = "6221D56E388D5D8317845E87"
TYPEBOT_ID = "assistente-cl-nica-teste-uk5j4sy"

sessions = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    print("WEBHOOK RECEBIDO!")
    print("BODY:", request.data)
    try:
        data = request.json
        if not data:
            return jsonify({"status": "ok"})

        phone = data.get("phone", "")
        message = data.get("text", {}).get("message", "")

        if not phone or not message:
            return jsonify({"status": "ok"})

        if phone not in sessions:
            response = requests.post(
                f"https://typebot.io/api/v1/typebots/{TYPEBOT_ID}/whatsapp/start",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
        else:
            session_id = sessions[phone]
            response = requests.post(
                f"https://typebot.io/api/v1/sessions/{session_id}/continueChat",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )

        print("Typebot status:", response.status_code)
        print("Typebot response:", response.text)

        if response.status_code != 200:
            return jsonify({"status": "ok"})

        result = response.json()
        
        if phone not in sessions:
            sessions[phone] = result.get("sessionId", "")

        messages = result.get("messages", [])
        for msg in messages:
            if msg.get("type") == "text":
                blocos = msg.get("content", {}).get("richText", [])
                for bloco in blocos:
                    for child in bloco.get("children", []):
                        texto = child.get("text", "")
                        if texto:
                            requests.post(
                                f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text",
                                json={"phone": phone, "message": texto}
                            )

    except Exception as e:
        print("Erro:", str(e))

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
