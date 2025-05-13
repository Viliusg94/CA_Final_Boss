"""
DB inicializavimo skriptas.
"""
import os
import sys
import logging

# Paprastas logeris
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("db_init")

def main():
    """Pagrindinis metodas"""
    # Gauname slaptažodį
    if len(sys.argv) > 1:
        password = sys.argv[1]
        logger.info("Slaptažodis gautas iš parametrų.")
    else:
        password = input("Įveskite MySQL slaptažodį: ")
        logger.info("Slaptažodis įvestas.")
    
    # Nustatome slaptažodį
    os.environ["DB_PASSWORD"] = password
    
    # Importuojame ir inicializuojame DB
    from database.init_db import initialize_database
    
    logger.info("====== BTC duomenų bazės inicializavimas ======")
    
    # Inicializuojame DB
    success = initialize_database()
    
    if success:
        logger.info("DB inicializacija SĖKMINGA!")
        logger.info("Galite naudotis BTC analizės sistema.")
    else:
        logger.error("DB inicializacija NEPAVYKO!")
        logger.error("Patikrinkite MySQL parametrus config.py faile.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
