"""
DB modeliai.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .config import Base, engine, SessionLocal

class BtcPrice(Base):
    """Bitcoin kainos"""
    __tablename__ = "btc_prices"
    
    id = Column(Integer, primary_key=True, index=True) 
    timestamp = Column(DateTime, nullable=False, index=True) 
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

class User(Base):
    """Naudotojai"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)
    
    uploads = relationship("UserUpload", back_populates="user")
    results = relationship("ModelResult", back_populates="user")

class UserUpload(Base):
    """Įkelti failai"""
    __tablename__ = "user_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="uploads")

class ModelResult(Base):
    """Modelių rezultatai"""
    __tablename__ = "model_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    execution_date = Column(DateTime, default=datetime.utcnow)
    mae = Column(Float, nullable=True)
    mse = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    r2 = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="results")

def test_connection():
    """DB prisijungimo testas"""
    try:
        session = SessionLocal()
        session.execute("SELECT 1")
        session.close()
        print("DB prisijungimas veikia!")
        return True
    except Exception as e:
        print(f"Klaida: {e}")
        return False

if __name__ == "__main__":
    print("===== DB testas =====")
    test_connection()
