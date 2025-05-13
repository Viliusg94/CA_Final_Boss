"""
Bitcoin duomenų analizės modulis.
Šis modulis sujungia kainos ir sentimento duomenų analizę.
"""

# Importuojame funkcijas iš apjungto bitcoin_analize.py failo
from .bitcoin_analize import (
    # Kainų funkcijos
    gauti_btc_kainas,
    prideti_rodiklius,
    paruosti_duomenis,
    
    # Sentimento funkcijos
    analizuoti_naujienu_sentimenta,
    prideti_sentimento_duomenis,
    
    # Pagrindinės funkcijos
    gauti_pilnus_btc_duomenis,
    issaugoti_i_duombaze
)

# Viešai prieinamos funkcijos
__all__ = [
    'gauti_btc_kainas',
    'prideti_rodiklius',
    'paruosti_duomenis',
    'analizuoti_naujienu_sentimenta',
    'prideti_sentimento_duomenis',
    'gauti_pilnus_btc_duomenis',
    'issaugoti_i_duombaze'
]