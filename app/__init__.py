from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from .extension import oauth
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI")

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    #this is needed to make sure that the app works correctly behind a reverse proxy like nginx, which is common in production environments. It ensures that the app can correctly determine the original request's protocol and host, which is important for generating correct URLs and handling redirects.
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_proto=1,
        x_host=1
    )
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

    oauth.init_app(app)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    from .scheduler import start_scheduler

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

    # Start the scheduler only when the app is not in debug mode or when the reloader is running. This prevents multiple instances of the scheduler from starting during development.
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            start_scheduler()

    return app