from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from app import db
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=False, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=False, nullable=False)
    ticket = relationship('Ticket', back_populates='user')


class Event(db.Model):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    event_name = Column(String, unique=True, nullable=False)
    event_description = Column(String, unique=False, nullable=False)
    total_tickets = Column(String, unique=False, nullable=False)
    ticket = relationship('Ticket', back_populates='event')


class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = Column(Integer, primary_key=True)
    status = Column(String, unique=False, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    user = relationship('User', back_populates='ticket')
    event = relationship('Event', back_populates='ticket')


class RegistrationForm(FlaskForm):
    email = EmailField(validators=[InputRequired(), Length(min=4, max=50)],
                           render_kw={'placeholder': 'Email'})

    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'Username'})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],
                           render_kw={'placeholder': 'Password'})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError('That email already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'Username'})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],
                           render_kw={'placeholder': 'Password'})

    submit = SubmitField('Login')
