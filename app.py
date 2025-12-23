from app import create_app
from flask import Flask
from app.routes.chatbot_routes import chatbot_bp

app = Flask(__name__)

app.register_blueprint(chatbot_bp, url_prefix="/api")

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
