from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from app import db


class User(db.Model):
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
    event_description = Column(String, unique=True, nullable=False)
    total_tickets = Column(String, unique=True, nullable=False)
    ticket = relationship('Ticket', back_populates='event')


class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = Column(Integer, primary_key=True)
    status = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    user = relationship('User', back_populates='ticket')
    event = relationship('Event', back_populates='ticket')

