"""
DB importų testavimas
"""

import os

# Testavimo rėžimas
os.environ["TEST_MODE"] = "True"

print("Testuojame duomenų bazės importus...")

try:
    # Importuojame bazines konfigūracijas
    print("Importuojame DB konfigūraciją...")
    from database import Base, engine, SessionLocal, get_db, DB_NAME
    print("  ✓ Konfigūracija importuota")
    
    # Importuojame modelius
    print("Importuojame DB modelius...")
    from database import BtcPrice, User, UserUpload, ModelResult
    print("  ✓ Modeliai importuoti")
    
    # Importuojame funkcijas
    print("Importuojame DB funkcijas...")
    from database import create_database, create_tables, initialize_database, test_connection
    print("  ✓ Funkcijos importuotos")
    
    print("\nVisi importai pavyko!")
    
    # Modelių tikrinimas
    print("\nModelių lentelių pavadinimai:")
    print(f"- BtcPrice: {BtcPrice.__tablename__}")
    print(f"- User: {User.__tablename__}")
    print(f"- UserUpload: {UserUpload.__tablename__}")
    print(f"- ModelResult: {ModelResult.__tablename__}")

except ImportError as e:
    print(f"Importo klaida: {e}")
except Exception as e:
    print(f"Klaida: {e}")

print("Testas baigtas.")
