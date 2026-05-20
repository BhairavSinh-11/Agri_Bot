from . import db
from flask_login import UserMixin
import bcrypt


# 👤 USER MODEL
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password=None, display_name=None, google_id=None):
        self.username = username
        self.display_name= display_name or username
        self.email = email.lower()
        if password:
         self.set_password(password)
        self.google_id = google_id 

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


# 💬 CHAT MODEL (IMPORTANT - OUTSIDE USER)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    response = db.Column(db.Text)
    image_path = db.Column(db.String(300), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
