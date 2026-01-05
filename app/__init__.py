# from flask import Flask, app
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_mail import Mail
# from flask_jwt_extended import JWTManager
# from config import Config
# from dotenv import load_dotenv
# load_dotenv()

# db = SQLAlchemy()
# migrate = Migrate()
# mail = Mail()
# jwt = JWTManager()

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     db.init_app(app)
#     migrate.init_app(app, db)
    

#     from app.models.user import User
#     from app.models.posture import PostureMeasurement
#     from app.models.diet import DietRecord

#     from app.auth.routes import auth_bp
#     from app.routes.user_routes import user_bp
#     from app.routes.posture_routes import posture_bp
#     from app.routes.diet_routes import diet_bp
#     from app.routes.chart_routes import chart_bp
#     from app.routes.admin_routes import admin_bp
#     from app.routes.chatbot_routes import chatbot_bp
    
#     app.register_blueprint(chatbot_bp)
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(user_bp)
#     app.register_blueprint(posture_bp)
#     app.register_blueprint(diet_bp)
#     app.register_blueprint(chart_bp)
#     app.register_blueprint(admin_bp)

#     return app
