from flask import Blueprint, request, jsonify
from app.chatbot.chatbot_engine import ChatbotPSC
import os

chatbot_bp = Blueprint("chatbot", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
KB_PATH = os.path.join(BASE_DIR, "chatbot", "knowledge_base.json")

chatbot = ChatbotPSC(KB_PATH)

@chatbot_bp.route("/chatbot", methods=["POST"])
def chatbot_api():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({
            "status": "error",
            "message": "Field 'message' is required"
        }), 400

    user_message = data["message"]
    response = chatbot.get_response(user_message)

    return jsonify({
        "status": "success",
        "data": {
            "question": user_message,
            "answer": response["answer"],
            "score": response["score"],
            "source": response["source"]
        }
    })
