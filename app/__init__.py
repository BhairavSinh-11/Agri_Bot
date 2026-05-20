from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from .extension import oauth

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

    oauth.init_app(app)
    
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    from .routes import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth)
    

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    return app