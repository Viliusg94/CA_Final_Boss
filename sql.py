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
    with engine.begin() as conn:
        df.to_sql('btc_ohlcv', con=conn, if_exists='append', index=False, method='multi')

# 7. Paleidžiam
if __name__ == "__main__":
    df = fetch_binance_ohlcv()
    print(df.head())
    save_to_db(df)
    print("Duomenys įrašyti į MySQL duomenų bazę.")
