"""
DB ryšio testas.
"""

import logging
from sqlalchemy import text
from .config import SessionLocal, DB_USER, DB_HOST, DB_NAME

# Paprastas logeris
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("db_test")

def test_connection():
    """Testuoja DB prisijungimą"""
    try:
        logger.info(f"Jungiamasi prie {DB_USER}@{DB_HOST}/{DB_NAME}...")
        session = SessionLocal()
        result = session.execute(text("SELECT 1")).fetchone()
        session.close()
        logger.info(f"DB veikia! Rezultatas: {result[0]}")
        return True
    except Exception as e:
        logger.error(f"Klaida: {e}")
        logger.info("Patikrinkite slaptažodį ir DB parametrus config.py faile")
        return False

if __name__ == "__main__":
    logger.info("===== DB prisijungimo testas =====")
    success = test_connection()
    if success:
        logger.info("Prisijungimas sėkmingas!")
    else:
        logger.error("Prisijungimas nepavyko!")
