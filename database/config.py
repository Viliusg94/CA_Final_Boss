"""
Duomenų bazės konfigūracija.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Prisijungimo duomenys iš MySQL lango
DB_USER = "root"  # Matome iš MySQL lango
DB_PASSWORD = os.environ.get("DB_PASSWORD", "final_boss")  # Slaptažodį imame iš aplinkos kintamųjų
DB_HOST = "localhost"  # Serveris
DB_PORT = "3306"  # Portas
DB_NAME = "BTC"  # DB pavadinimas

# URL - naudojame mysql-connector-python
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Sukuriame SQLAlchemy objektus
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """DB sesija"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Sukuria duomenų bazėje visas lenteles pagal ORM modelius.
    """
    # Importuojame visus modelius, kad būtų užregistruoti su Base
    from database.models import BtcPrice, User, UserUpload, ModelResult, BtcOHLCV, BtcFeatures, MLModel
    
    # Sukuriame lenteles
    Base.metadata.create_all(bind=engine)
    print("Duomenų bazės lentelės sukurtos!")
    return True