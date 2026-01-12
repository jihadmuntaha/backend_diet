from flask import Flask
from flask_cors import CORS
from app.services.article_fetcher import fetch_all_articles
from config import Config, db, mail, jwt, migrate, template_dir
from dotenv import load_dotenv
from app.auth.routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.posture_routes import posture_bp
from app.routes.diet_routes import diet_bp
from app.routes.chart_routes import chart_bp
from app.routes.admin_routes import admin_bp
from app.routes.chatbot_routes import chatbot_bp
from app.routes.article_routes import article_bp
from app.tasks.scheduler import start_scheduler
from api.routes import api_detect_bp, api_auth_bp, api_bp
from models.users import Users
from models.alergi import Alergi
from models.user_health import UserHealth
from models.posture_scan import PostureScan
from models.recomendation import Recommendations
from models.user_reviews import UserReview

load_dotenv()
app = Flask(__name__, template_folder=template_dir)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

db.init_app(app)
mail.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)
start_scheduler()

app.register_blueprint(chatbot_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(posture_bp)
app.register_blueprint(diet_bp)
app.register_blueprint(chart_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_detect_bp)
app.register_blueprint(api_auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(article_bp)

with app.app_context():
    fetch_all_articles()
    db.create_all()

if __name__ == "__main__":
    app.run()
