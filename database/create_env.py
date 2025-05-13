"""
DB aplinkos kintamieji.
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("env")

def create_environment_variables():
    """DB aplinkos kintamieji"""
    # DB parametrai
    db_vars = {
        "DB_USER": "root", 
        "DB_PASSWORD": "final_boss",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_NAME": "BTC"
    }
    
    # Nustatymas
    for key, value in db_vars.items():
        os.environ[key] = value
        logger.info(f"Nustatytas {key}")
    
    return True

if __name__ == "__main__":
    create_environment_variables()
    logger.info("Kintamieji nustatyti")