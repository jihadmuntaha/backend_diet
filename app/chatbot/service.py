import os
from app.chatbot.chatbot_engine import ChatbotModel

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_PATH = os.path.join(
    BASE_DIR, "chatbot", "dataset", "playstore_reviews.csv"
)

# Load model ONCE (important for performance)
chatbot_model = ChatbotModel(DATASET_PATH)


def generate_reply(message: str) -> str:
    """
    Generate chatbot reply from user message
    """
    return chatbot_model.get_response(message)
