# models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from App.Config.database import Base  # Import Base from database.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Newly added column
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, default=datetime.utcnow)
