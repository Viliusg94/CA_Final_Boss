"""
DB išvalymo skriptas.
Šis skriptas išvalo duomenų bazę ir sukuria ją iš naujo.
"""
import os
import sys
import logging
import mysql.connector

# Paprastas logeris
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("db_reset")

def reset_database():
    """Išvalo ir iš naujo inicializuoja duomenų bazę"""
    # Importuojame konfigūraciją
    from database.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
    
    try:
        # Prisijungiame prie serverio
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Ištriname DB, jei ji egzistuoja
        logger.info(f"Ištrinama duomenų bazė {DB_NAME}...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        logger.info("Duomenų bazė ištrinta.")
        
        # Uždarome prisijungimą
        cursor.close()
        conn.close()
        
        # Sukuriame DB iš naujo
        from database.init_db import initialize_database
        if initialize_database():
            logger.info("DB sėkmingai iš naujo inicializuota!")
            return True
        else:
            logger.error("Klaida inicializuojant DB!")
            return False
            
    except Exception as e:
        logger.error(f"Klaida: {e}")
        return False

def main():
    """Pagrindinis metodas"""
    # Gauname slaptažodį
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Įveskite MySQL slaptažodį: ")
    
    # Patvirtinimas
    confirm = input("DĖMESIO! Jūs ketinate ištrinti visus duomenis! Patvirtinkite (y/n): ")
    if confirm.lower() != "y":
        logger.info("Operacija atšaukta.")
        return 0
    
    # Nustatome slaptažodį
    os.environ["DB_PASSWORD"] = password
    
    logger.info("====== BTC duomenų bazės išvalymas ======")
    
    # Išvalome DB
    success = reset_database()
    
    if success:
        logger.info("DB išvalymas ir inicializacija SĖKMINGA!")
    else:
        logger.error("DB išvalymas ir inicializacija NEPAVYKO!")
        logger.error("Patikrinkite MySQL parametrus config.py faile.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
