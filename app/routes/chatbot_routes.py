from flask import Blueprint, request, jsonify
from app.services.chatbot_service import get_chatbot_reply

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot_api():
    data = request.get_json() or {}
    message = data.get("message")

    if not message:
        return jsonify({"message": "Message is required"}), 400

    reply = get_chatbot_reply(message)

    return jsonify({
        "question": message,
        "reply": reply
    }), 200
