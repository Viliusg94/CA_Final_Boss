"""
Duomenų transformacijos modulis - čia atliekame visus duomenų 
apdorojimo veiksmus, naudojant SQLAlchemy ORM
"""
import pandas as pd
import numpy as np
import os
import sys
import logging
from datetime import datetime

# Šis kelias leidžia importuoti modulius iš kitų direktorijų
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Importuojame duomenų bazės prisijungimą
from database.config import engine, SessionLocal
# Importuojame duomenų bazės modelius
from database.models import BtcOHLCV, BtcFeatures
# Importuojame techninių indikatorių skaičiavimo funkcijas
from features.technical_indicators import create_all_features

# Sukuriame logerį
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("data_transformer")

def get_ohlcv_data():
    """
    Ši funkcija paima BTC kainos duomenis iš duomenų bazės naudojant SQLAlchemy ORM
    
    Grąžina:
        DataFrame su OHLCV (Open-High-Low-Close-Volume) duomenimis
    """
    try:
        # Sukuriame sesiją
        session = SessionLocal()
        
        # Naudojame ORM užklausą vietoj raw SQL
        # query() metodas leidžia mums naudoti ORM klasę tiesiogiai
        ohlcv_records = session.query(BtcOHLCV).order_by(BtcOHLCV.timestamp).all()
        
        # Konvertuojame ORM objektus į DataFrame
        data = []
        for record in ohlcv_records:
            # Kiekvienas record yra BtcOHLCV objektas, kurį konvertuojame į žodyną
            data.append({
                'timestamp': record.timestamp,
                'open': record.open,
                'high': record.high,
                'low': record.low,
                'close': record.close,
                'volume': record.volume
            })
        
        # Sukuriame DataFrame iš duomenų sąrašo
        df = pd.DataFrame(data)
        
        # Uždarome sesiją
        session.close()
        
        # Išvedame informaciją kiek eilučių gavome
        logger.info(f"Iš DB gauta {len(df)} OHLCV eilučių")
        return df
    except Exception as e:
        # Jei įvyko klaida - išvedame klaidą
        logger.error(f"Klaida gaunant duomenis: {e}")
        # Užtikriname, kad sesija būtų uždaryta net jei įvyko klaida
        if 'session' in locals():
            session.close()
        # Grąžiname tuščią DataFrame
        return pd.DataFrame()

def save_features_to_db(df, table_name='btc_features'):
    """
    Ši funkcija įrašo apskaičiuotus techninius indikatorius į duomenų bazę
    naudojant SQLAlchemy ORM objektus
    
    Parametrai:
        df: DataFrame su techniniais indikatoriais
        table_name: Lentelės pavadinimas duomenų bazėje
    
    Grąžina:
        bool: True jei pavyko, False jei nepavyko
    """
    try:
        # Sukuriame sesiją
        session = SessionLocal()
        
        # Ištriname visus senus įrašus - naudojame ORM
        session.query(BtcFeatures).delete()
        session.commit()
        logger.info(f"Lentelė {table_name} išvalyta")
        
        # Įrašome naujus duomenis po vieną eilutę
        records_added = 0
        for _, row in df.iterrows():
            # Sukuriame naują BtcFeatures objektą pagal mūsų ORM modelį
            feature_record = BtcFeatures(
                timestamp=row['timestamp'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume'],
                
                # SMA
                sma_5=row.get('sma_5'),
                sma_10=row.get('sma_10'),
                sma_20=row.get('sma_20'),
                sma_50=row.get('sma_50'),
                sma_200=row.get('sma_200'),
                
                # EMA
                ema_5=row.get('ema_5'),
                ema_10=row.get('ema_10'),
                ema_20=row.get('ema_20'),
                ema_50=row.get('ema_50'),
                ema_200=row.get('ema_200'),
                
                # RSI
                rsi_14=row.get('rsi_14'),
                
                # MACD
                macd=row.get('macd'),
                macd_signal=row.get('macd_signal'),
                macd_histogram=row.get('macd_histogram'),
                
                # Bollinger Bands
                bb_middle=row.get('bb_middle'),
                bb_upper=row.get('bb_upper'),
                bb_lower=row.get('bb_lower'),
                bb_width=row.get('bb_width'),
                
                # Lag features
                close_lag_1=row.get('close_lag_1'),
                close_lag_2=row.get('close_lag_2'),
                close_lag_3=row.get('close_lag_3'),
                close_lag_5=row.get('close_lag_5'),
                close_lag_7=row.get('close_lag_7'),
                close_lag_14=row.get('close_lag_14'),
                close_lag_21=row.get('close_lag_21'),
                
                return_lag_1=row.get('return_lag_1'),
                return_lag_2=row.get('return_lag_2'),
                return_lag_3=row.get('return_lag_3'),
                return_lag_5=row.get('return_lag_5'),
                return_lag_7=row.get('return_lag_7'),
                return_lag_14=row.get('return_lag_14'),
                return_lag_21=row.get('return_lag_21'),
                
                # Target
                target=row.get('target')
            )
            
            # Pridedame objektą į sesiją
            session.add(feature_record)
            records_added += 1
            
            # Komituojame kas 100 įrašų, kad neperkrauti atminties
            if records_added % 100 == 0:
                session.commit()
                logger.info(f"Įrašyta {records_added} eilučių...")
        
        # Galutinis komitas
        session.commit()
        session.close()
        
        logger.info(f"Į lentelę {table_name} įrašyta {records_added} eilučių")
        return True
    except Exception as e:
        logger.error(f"Klaida įrašant duomenis: {e}")
        # Atšaukiame pakeitimus jei buvo klaida
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def create_and_save_features():
    """
    Pagrindinė funkcija, kuri:
    1. Gauna duomenis iš duomenų bazės
    2. Apskaičiuoja techninius indikatorius
    3. Įrašo rezultatus į duomenų bazę
    
    Grąžina:
        bool: True jei pavyko, False jei nepavyko
    """
    # Pirmas žingsnis - gauname pradinius duomenis
    df = get_ohlcv_data()
    
    # Patikriname ar gavome duomenis
    if df.empty:
        logger.error("Nepavyko gauti duomenų - DataFrame tuščias")
        return False
    
    # Antras žingsnis - skaičiuojame techninius indikatorius
    logger.info("Pradedame skaičiuoti techninius indikatorius...")
    
    # Kviečiame funkciją, kuri pridės visus indikatorius
    df_features = create_all_features(df)
    logger.info(f"Apskaičiuota {len(df_features)} eilučių su {len(df_features.columns)} stulpeliais")
    
    # Trečias žingsnis - įrašome duomenis į duomenų bazę
    logger.info("Įrašome duomenis į duomenų bazę...")
    
    # Kviečiame funkciją, kuri įrašys duomenis
    success = save_features_to_db(df_features)
    
    # Patikriname ar pavyko įrašyti
    if success:
        logger.info("Viskas pavyko! Duomenų transformacija baigta!")
    else:
        logger.error("Kažkas nepavyko įrašant duomenis!")
    
    return success

# Šis kodas bus vykdomas tik jei paleisime šį failą tiesiogiai
if __name__ == "__main__":
    logger.info("===== Pradedama duomenų transformacija =====")
    # Paleidžiame pagrindinę funkciją
    create_and_save_features()