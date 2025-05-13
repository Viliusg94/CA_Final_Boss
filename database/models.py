"""
DB modeliai su ORM.
Apibrėžia duomenų bazės struktūrą ir ryšius tarp lentelių.
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

class BtcOHLCV(Base):
    """Bitcoin OHLCV duomenys (naujas modelis techninei analizei)"""
    __tablename__ = 'btc_ohlcv'
    
    timestamp = Column(DateTime, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    def __repr__(self):
        """Kaip atvaizduojamas objektas spausdinant"""
        return f"<BtcOHLCV(timestamp='{self.timestamp}', close={self.close})>"


class BtcFeatures(Base):
    """Bitcoin techniniai indikatoriai (naujas modelis)"""
    __tablename__ = 'btc_features'
    
    # Pagrindiniai duomenys
    timestamp = Column(DateTime, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Techniniai indikatoriai
    # Slankieji vidurkiai (SMA)
    sma_5 = Column(Float)
    sma_10 = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    
    # Eksponentiniai slankieji vidurkiai (EMA)
    ema_5 = Column(Float)
    ema_10 = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    ema_200 = Column(Float)
    
    # RSI indikatorius
    rsi_14 = Column(Float)
    
    # MACD indikatorius
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    
    # Bollinger Bands
    bb_middle = Column(Float)
    bb_upper = Column(Float)
    bb_lower = Column(Float)
    bb_width = Column(Float)
    
    # Ankstesnių periodų kainos
    close_lag_1 = Column(Float)
    close_lag_2 = Column(Float)
    close_lag_3 = Column(Float)
    close_lag_5 = Column(Float)
    close_lag_7 = Column(Float)
    close_lag_14 = Column(Float)
    close_lag_21 = Column(Float)
    
    # Ankstesnių periodų grąžos
    return_lag_1 = Column(Float)
    return_lag_2 = Column(Float)
    return_lag_3 = Column(Float)
    return_lag_5 = Column(Float)
    return_lag_7 = Column(Float)
    return_lag_14 = Column(Float)
    return_lag_21 = Column(Float)
    
    # Tikslo kintamasis (1-kils, 0-kris)
    target = Column(Integer)
    
    def __repr__(self):
        """Kaip atvaizduojamas objektas spausdinant"""
        return f"<BtcFeatures(timestamp='{self.timestamp}', target={self.target})>"


class MLModel(Base):
    """Mašininio mokymosi modelių saugojimas"""
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    model_path = Column(String(255))
    
    def __repr__(self):
        """Kaip atvaizduojamas objektas spausdinant"""
        return f"<MLModel(id={self.id}, name='{self.name}', accuracy={self.accuracy})>"

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
