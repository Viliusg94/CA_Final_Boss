"""
Duomenų bazės inicializavimo modulis.
"""

import mysql.connector
import logging
from sqlalchemy import text
from .config import engine, Base, DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

# Paprastas logeris
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("db_init")

def create_database():
    """Sukuria DB"""
    try:
        # Prisijungimas
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # DB sukūrimas
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        logger.info(f"DB '{DB_NAME}' sukurta")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Klaida: {e}")
        return False

def create_tables():
    """Sukuria lenteles"""
    try:
        from .models import BtcPrice, User, UserUpload, ModelResult
        Base.metadata.create_all(bind=engine)
        logger.info("Lentelės sukurtos")
        return True
    except Exception as e:
        logger.error(f"Klaida: {e}")
        return False

def initialize_database():
    """Inicializuoja DB"""
    logger.info("DB inicializacija...")
    if create_database():
        if create_tables():
            logger.info("DB inicializuota")
            return True
    logger.error("DB inicializacija nepavyko")
    return False

if __name__ == "__main__":
    initialize_database()