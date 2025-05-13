"""
Skriptas MySQL slaptažodžio nustatymui.
"""
import os
import sys

def set_password():
    """Nustatome MySQL slaptažodį"""
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Įveskite MySQL slaptažodį: ")
    
    os.environ["DB_PASSWORD"] = password
    print(f"Slaptažodis nustatytas aplinkos kintamiesiems.")
    
    # Bandomai paleisti testą
    from database.test_connection import test_connection
    test_connection()

if __name__ == "__main__":
    set_password()
