from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    # Prefix 'college_' ensures isolation in the shared database.
    # This prevents conflicts with other tables (e.g., from the portfolio project)
    # residing in the same PostgreSQL instance.
    __tablename__ = "college_users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

    registrations = relationship("Registration", back_populates="user")

class Event(Base):
    __tablename__ = "college_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    date_time = Column(DateTime)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    registrations = relationship("Registration", back_populates="event")

class Registration(Base):
    __tablename__ = "college_registrations"
    __table_args__ = (UniqueConstraint('user_id', 'event_id', name='uq_user_event'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("college_users.id"))
    event_id = Column(Integer, ForeignKey("college_events.id"))
    registration_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
