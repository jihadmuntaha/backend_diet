from app.chatbot.chatbot_engine import ChatbotModel
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_PATH = os.path.join(
    BASE_DIR, "chatbot", "dataset", "playstore_reviews.csv"
)

chatbot_model = ChatbotModel(DATASET_PATH)


def get_chatbot_reply(message: str) -> str:
    return chatbot_model.get_response(message)
