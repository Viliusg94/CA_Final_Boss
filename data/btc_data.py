"""
Bitcoin kainų duomenų gavimas ir apdorojimas.
Šis modulis gauna Bitcoin kainas ir skaičiuoja techninius rodiklius.
"""

# ----- IMPORTAI -----
import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
from datetime import datetime
import logging

# Logerio nustatymai
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("btc_data")

# ----- KONSTANTOS -----
BTC_SYMBOL = "BTC-USD"
DEFAULT_PERIOD = "2y"
DEFAULT_INTERVAL = "1d"

def gauti_btc_kainas(pradzia=None, pabaiga=None, periodas=DEFAULT_PERIOD, intervalas=DEFAULT_INTERVAL):
    """Gauna Bitcoin kainas iš Yahoo Finance API"""
    try:
        logger.info("Gaunami BTC kainų duomenys...")
        
        # Gauname duomenis pagal nurodytas datas arba periodą
        if pradzia and pabaiga:
            duomenys = yf.download(BTC_SYMBOL, start=pradzia, end=pabaiga, interval=intervalas)
        else:
            duomenys = yf.download(BTC_SYMBOL, period=periodas, interval=intervalas)
        
        # Tikriname ar gavome duomenis
        if duomenys.empty:
            logger.error("Nepavyko gauti BTC kainų duomenų")
            return pd.DataFrame()
        
        # Atnaujiname indeksą
        duomenys = duomenys.reset_index()
        
        # Pervardijame stulpelį jei reikia
        if 'Datetime' in duomenys.columns:
            duomenys = duomenys.rename(columns={'Datetime': 'Date'})
        
        logger.info(f"Gauti {len(duomenys)} BTC kainų įrašai")
        return duomenys
    
    except Exception as e:
        logger.error(f"Klaida gaunant BTC duomenis: {e}")
        return pd.DataFrame()

def prideti_slankiuosius_vidurkius(duomenys, trumpas=7, vidutinis=30, ilgas=90):
    """Prideda slankiuosius vidurkius"""
    try:
        df = duomenys.copy()
        
        # Tikriname ar yra reikalingas stulpelis
        if 'Close' not in df.columns:
            logger.error("Duomenyse nėra 'Close' stulpelio")
            return duomenys
        
        # Paprasti slankieji vidurkiai (SMA)
        for periodas in [trumpas, vidutinis, ilgas]:
            df[f'SMA_{periodas}'] = SMAIndicator(close=df['Close'], window=periodas).sma_indicator()
        
        # Eksponentiniai slankieji vidurkiai (EMA)
        for periodas in [trumpas, vidutinis]:
            df[f'EMA_{periodas}'] = EMAIndicator(close=df['Close'], window=periodas).ema_indicator()
        
        logger.info("Pridėti slankieji vidurkiai")
        return df
    
    except Exception as e:
        logger.error(f"Klaida pridedant slankiuosius vidurkius: {e}")
        return duomenys

def prideti_technines_indikacijas(duomenys):
    """Prideda RSI, MACD, Bollinger juostas"""
    try:
        df = duomenys.copy()
        
        # Tikriname ar yra reikalingas stulpelis
        if 'Close' not in df.columns:
            logger.error("Duomenyse nėra 'Close' stulpelio")
            return duomenys
        
        # RSI (14 dienų)
        df['RSI_14'] = RSIIndicator(close=df['Close'], window=14).rsi()
        
        # MACD
        macd = MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Histogram'] = macd.macd_diff()
        
        # Bollinger juostos
        bollinger = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Mid'] = bollinger.bollinger_mavg()
        df['BB_Low'] = bollinger.bollinger_lband()
        
        logger.info("Pridėtos techninės indikacijos")
        return df
    
    except Exception as e:
        logger.error(f"Klaida pridedant technines indikacijas: {e}")
        return duomenys

def prideti_kainų_pokyčius(duomenys):
    """Prideda kainų pokyčių rodiklius"""
    try:
        df = duomenys.copy()
        
        # Tikriname ar yra reikalingi stulpeliai
        if 'Close' not in df.columns or 'Volume' not in df.columns:
            logger.error("Trūksta reikalingų stulpelių")
            return duomenys
        
        # Kainų pokyčiai
        df['Price_Change'] = df['Close'].diff()  # Absoliutus pokytis
        df['Price_Change_Pct'] = df['Close'].pct_change() * 100  # Procentinis pokytis
        
        # Grąžos rodikliai
        df['Return_7d'] = df['Close'].pct_change(periods=7) * 100
        df['Return_30d'] = df['Close'].pct_change(periods=30) * 100
        
        # Kintamumas
        df['Volatility_30d'] = df['Price_Change_Pct'].rolling(window=30).std()
        
        # Apimties (Volume) rodikliai
        df['Volume_Change'] = df['Volume'].pct_change() * 100
        df['Volume_SMA_7'] = df['Volume'].rolling(window=7).mean()
        
        logger.info("Pridėti kainų pokyčių rodikliai")
        return df
    
    except Exception as e:
        logger.error(f"Klaida pridedant pokyčių rodiklius: {e}")
        return duomenys

def paruosti_duomenis(pradzia=None, pabaiga=None, periodas=DEFAULT_PERIOD, intervalas=DEFAULT_INTERVAL):
    """Paruošia BTC duomenis su visais rodikliais"""
    # Gauname pradinius duomenis
    df = gauti_btc_kainas(pradzia, pabaiga, periodas, intervalas)
    
    if df.empty:
        logger.error("Negauti BTC duomenys")
        return df
    
    # Pridedame rodiklius
    df = prideti_slankiuosius_vidurkius(df)
    df = prideti_technines_indikacijas(df)
    df = prideti_kainų_pokyčius(df)
    
    # Pašaliname trūkstamas reikšmes
    df = df.dropna()
    
    logger.info(f"Sėkmingai paruošti {len(df)} įrašai")
    return df

def issaugoti_i_duombaze(duomenys, db_session):
    """Išsaugo duomenis į duomenų bazę"""
    try:
        from database.models import BtcPrice
        
        # Išsaugome duomenis
        įrašų_skaičius = 0
        
        for _, eilute in duomenys.iterrows():
            # Sukuriame naują įrašą
            btc_kaina = BtcPrice(
                timestamp=eilute['Date'],
                open=eilute['Open'],
                high=eilute['High'],
                low=eilute['Low'],
                close=eilute['Close'],
                volume=eilute['Volume']
            )
            
            # Pridedame į sesiją
            db_session.add(btc_kaina)
            įrašų_skaičius += 1
        
        # Įrašome pakeitimus
        db_session.commit()
        logger.info(f"Išsaugoti {įrašų_skaičius} įrašai į DB")
        return True
    
    except Exception as e:
        db_session.rollback()
        logger.error(f"Klaida išsaugant į DB: {e}")
        return False

# Jei šis failas vykdomas tiesiogiai
if __name__ == "__main__":
    # Gauname duomenis
    duomenys = paruosti_duomenis(periodas="2y", intervalas="1d")
    
    # Parodome rezultatus
    if not duomenys.empty:
        print(duomenys.head())
        duomenys.to_csv("btc_data_with_indicators.csv", index=False)
        print(f"Duomenys išsaugoti: btc_data_with_indicators.csv")
    else:
        print("Nepavyko gauti duomenų.")