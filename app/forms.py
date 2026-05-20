from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')
    ])

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already exists")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data.lower()).first():
            raise ValidationError("Email already exists")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class ForgotResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    password = PasswordField('New Password', validators=[
        DataRequired(), Length(min=6)
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')
    ])