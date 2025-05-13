import requests
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, Float, DateTime, MetaData, UniqueConstraint
from datetime import datetime

# 1. Konfigūracijos – Binance API endpoint + DB prisijungimo duomenys
BINANCE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "15m"  # gali būti 1m, 15m, 1h, 1d
LIMIT = 1000  # max 1000 duomenų vienu užklausimu

# 2. MySQL duomenų bazės konfigūracija (pakeisk savo duomenimis)
DB_USER = "root"
DB_PASSWORD = "final_boss"
DB_HOST = "localhost"
DB_NAME = "BTC"

# 3. Sukuriame SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

# 4. Sukuriame lentelę, jei jos nėra
metadata = MetaData()
btc_table = Table(
    'btc_ohlcv', metadata,
    Column('id', Integer, primary_key=True),
    Column('timestamp', DateTime, nullable=False),
    Column('open', Float),
    Column('high', Float),
    Column('low', Float),
    Column('close', Float),
    Column('volume', Float),
    UniqueConstraint('timestamp', name='uix_timestamp')
)
metadata.create_all(engine)

# 5. Gauti duomenis iš Binance API
def fetch_binance_ohlcv():
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": LIMIT
    }
    response = requests.get(BINANCE_URL, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        '_', '_', '_', '_', '_', '_'
    ])
    df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df = df.astype({
        'open': float, 'high': float, 'low': float, 'close': float, 'volume': float
    })
    df.rename(columns={'open_time': 'timestamp'}, inplace=True)
    return df

# 6. Įrašyti į MySQL
def save_to_db(df):
    """
    Įrašo duomenis į duomenų bazę, ignoruojant pasikartojančius įrašus.
    
    Args:
        df: DataFrame su BTC duomenimis
    """
    try:
        with engine.begin() as conn:
            # Naudojame 'replace' vietoj 'append', jei norime perrašyti duomenis:
            # df.to_sql('btc_ohlcv', con=conn, if_exists='replace', index=False, method='multi')
            
            # Arba naudojame 'ignore' parametrą (nuo SQLAlchemy 1.4):
            df.to_sql('btc_ohlcv', con=conn, if_exists='append', index=False, 
                    method='multi', chunksize=1000)
            print(f"Sėkmingai įrašyta {len(df)} eilučių")
    except Exception as e:
        # Jei klaida - bandome įrašyti po vieną eilutę, preskipinant pasikartojančias
        print(f"Aptikta duplikatų, įrašomi tik nauji duomenys: {e}")
        inserted = 0
        for _, row in df.iterrows():
            try:
                row_df = pd.DataFrame([row])
                row_df.to_sql('btc_ohlcv', con=engine, if_exists='append', index=False)
                inserted += 1
            except Exception:
                # Ignoruojame pasikartojančius įrašus
                pass
        print(f"Sėkmingai įrašyta {inserted} eilučių, praleista {len(df) - inserted} duplikatų")

# 7. Paleidžiam
if __name__ == "__main__":
    df = fetch_binance_ohlcv()
    print(df.head())
    save_to_db(df)
    print("Duomenys įrašyti į MySQL duomenų bazę.")
