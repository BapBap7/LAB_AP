from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    ticket = relationship('Ticket', back_populates='user')


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    event_name = Column(String, unique=True, nullable=False)
    event_description = Column(String, unique=True, nullable=False)
    total_tickets = Column(String, unique=True, nullable=False)
    ticket = relationship('Ticket', back_populates='event')


class Ticket(Base):
    __tablename__ = 'ticket'
    id = Column(Integer, primary_key=True)
    status = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    user = relationship('User', back_populates='ticket')
    event = relationship('Event', back_populates='ticket')

