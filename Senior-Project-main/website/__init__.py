from flask import Flask as fs
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app(secrete_key: str = None):
    app = fs(__name__)
    
    # Use environment variable for secret key if not provided
    app.secret_key = secrete_key or os.getenv('SECRET_KEY', 'fallback-secret-key')
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///vacation_genie.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    from .models import db
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app