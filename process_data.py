"""
Duomenų apdorojimo ir transformacijos pagrindinis skriptas
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# Pakeičiame importą į tiesioginį
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.test_connection import test_connection
from database.config import create_tables
from features.data_transformer import create_and_save_features
from ml.model_trainer import train_model

# Logeris
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("process_data")

def main():
    """
    Pagrindinis duomenų apdorojimo metodas
    """
    parser = argparse.ArgumentParser(description="BTC duomenų apdorojimas")
    parser.add_argument("--transform", action="store_true", help="Transformuoti duomenis")
    parser.add_argument("--train", action="store_true", help="Treniruoti ML modelį")
    parser.add_argument("--setup-db", action="store_true", help="Sukurti duomenų bazės lenteles")
    args = parser.parse_args()
    
    # Tikriname DB ryšį
    logger.info("Tikriname DB ryšį...")
    if not test_connection():
        logger.error("Nepavyko prisijungti prie DB. Procesai nutraukiami.")
        return
    
    # Sukuriame DB lenteles, jei reikia
    if args.setup_db:
        logger.info("Kuriamos duomenų bazės lentelės...")
        create_tables()
        logger.info("Duomenų bazės lentelės sukurtos!")
    
    # Duomenų transformacija
    if args.transform:
        logger.info("Pradedama duomenų transformacija...")
        if create_and_save_features():
            logger.info("Duomenų transformacija sėkmingai baigta!")
        else:
            logger.error("Duomenų transformacija nepavyko!")
    
    # Modelio treniravimas
    if args.train:
        logger.info("Pradedamas modelio treniravimas...")
        if train_model():
            logger.info("Modelio treniravimas sėkmingai baigtas!")
        else:
            logger.error("Modelio treniravimas nepavyko!")
    
    # Jei nebuvo nurodyta jokių veiksmų
    if not (args.transform or args.train or args.setup_db):
        logger.info("Naudokite --transform duomenų transformacijai")
        logger.info("Naudokite --train modelio treniravimui")
        logger.info("Naudokite --setup-db duomenų bazės lentelių sukūrimui")
        logger.info("Pavyzdys: python process_data.py --transform --train")
    
    logger.info("Darbas baigtas!")

if __name__ == "__main__":
    logger.info(f"===== BTC duomenų apdorojimo pradžia: {datetime.now()} =====")
    main()
    logger.info(f"===== BTC duomenų apdorojimo pabaiga: {datetime.now()} =====")