"""
Techninių indikatorių skaičiavimo modulis
"""
import pandas as pd
import numpy as np

def add_moving_averages(df, windows=[5, 10, 20, 50, 200]):
    """
    Prideda paprastus slankiuosius vidurkius (SMA) prie duomenų.
    
    Parametrai:
        df: DataFrame su 'close' stulpeliu
        windows: Periodų sąrašas
    """
    df = df.copy()
    # Skaičiuojame SMA kiekvienam nurodytam periodui
    for window in windows:
        df[f'sma_{window}'] = df['close'].rolling(window=window).mean()
    return df

def add_exponential_moving_averages(df, windows=[5, 10, 20, 50, 200]):
    """
    Prideda eksponentinius slankiuosius vidurkius (EMA) prie duomenų.
    
    Parametrai:
        df: DataFrame su 'close' stulpeliu
        windows: Periodų sąrašas
    """
    df = df.copy()
    # Skaičiuojame EMA kiekvienam nurodytam periodui
    for window in windows:
        df[f'ema_{window}'] = df['close'].ewm(span=window, adjust=False).mean()
    return df

def add_rsi(df, window=14):
    """
    Prideda reliatyvios jėgos indeksą (RSI) prie duomenų.
    
    Parametrai:
        df: DataFrame su 'close' stulpeliu
        window: Periodų skaičius
    """
    df = df.copy()
    # Skaičiuojame kainos pokyčius
    delta = df['close'].diff()
    
    # Atskirame teigiamus ir neigiamus pokyčius
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Skaičiuojame vidurkius
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    # Skaičiuojame RS (Relative Strength)
    rs = avg_gain / avg_loss
    
    # Skaičiuojame RSI
    df[f'rsi_{window}'] = 100 - (100 / (1 + rs))
    return df

def add_macd(df, fast=12, slow=26, signal=9):
    """
    Prideda MACD (Moving Average Convergence Divergence) prie duomenų.
    
    Parametrai:
        df: DataFrame su 'close' stulpeliu
        fast: Greito EMA periodas
        slow: Lėto EMA periodas
        signal: Signalo linijos periodas
    """
    df = df.copy()
    
    # Skaičiuojame greitą ir lėtą EMA
    fast_ema = df['close'].ewm(span=fast, adjust=False).mean()
    slow_ema = df['close'].ewm(span=slow, adjust=False).mean()
    
    # MACD linija = greitas EMA - lėtas EMA
    df['macd'] = fast_ema - slow_ema
    
    # Signalo linija = MACD EMA
    df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    
    # MACD histograma = MACD - Signalo linija
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df

def add_bollinger_bands(df, window=20, num_std=2):
    """
    Prideda Bollinger juostas prie duomenų.
    
    Parametrai:
        df: DataFrame su 'close' stulpeliu
        window: Periodų skaičius vidurkiui
        num_std: Standartinių nuokrypių skaičius juostoms
    """
    df = df.copy()
    
    # Vidurinė juosta = SMA
    df['bb_middle'] = df['close'].rolling(window=window).mean()
    
    # Standartinis nuokrypis
    df['bb_std'] = df['close'].rolling(window=window).std()
    
    # Viršutinė juosta = SMA + (STD * n)
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * num_std)
    
    # Apatinė juosta = SMA - (STD * n)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * num_std)
    
    # Juostų plotis = (Viršutinė - Apatinė) / Vidurinė
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    # Pašaliname tarpinį stulpelį
    df.drop('bb_std', axis=1, inplace=True)
    
    return df

def add_lag_features(df, lags=[1, 2, 3, 5, 7, 14, 21]):
    """
    Prideda ankstesnių periodų (lag) kainų ir grąžų features.
    
    Parametrai:
        df: DataFrame su 'close' stulpeliu
        lags: Lag periodų sąrašas
    """
    df = df.copy()
    
    # Kiekvienam lag periodui pridedame kainos ir grąžos stulpelius
    for lag in lags:
        # Ankstesnių periodų kainos
        df[f'close_lag_{lag}'] = df['close'].shift(lag)
        
        # Ankstesnių periodų grąžos (procentiniai pokyčiai)
        df[f'return_lag_{lag}'] = df['close'].pct_change(lag)
    
    return df

def add_target_label(df, forward_periods=1):
    """
    Prideda tikslo (target) kintamąjį: 1 jei kaina kils, 0 jei kris.
    
    Parametrai:
        df: DataFrame su 'close' stulpeliu
        forward_periods: Periodų skaičius į priekį
    """
    df = df.copy()
    
    # Ateities kaina (po nurodytų periodų)
    df['future_price'] = df['close'].shift(-forward_periods)
    
    # Target: 1 jei ateities kaina didesnė už dabartinę, 0 jei mažesnė
    df['target'] = (df['future_price'] > df['close']).astype(int)
    
    # Pašaliname tarpinį stulpelį
    df.drop('future_price', axis=1, inplace=True)
    
    return df

def normalize_features(df, exclude_cols=['timestamp', 'target']):
    """
    Normalizuoja visus features (išskyrus nurodytus).
    
    Parametrai:
        df: DataFrame su features
        exclude_cols: Stulpelių sąrašas, kurių nereikia normalizuoti
    """
    df = df.copy()
    
    # Normalizuojame tik reikiamus stulpelius
    for col in df.columns:
        if col not in exclude_cols:
            # Skaičiuojame vidurkį ir standartinį nuokrypį
            mean = df[col].mean()
            std = df[col].std()
            
            # Tikriname ar standartinis nuokrypis nėra 0
            if std > 0:
                # Z-score normalizacija: (x - mean) / std
                df[f'{col}_norm'] = (df[col] - mean) / std
    
    return df

def create_all_features(df):
    """
    Prideda visus techninius indikatorius ir features į vieną DataFrame.
    
    Parametrai:
        df: DataFrame su pradiniais duomenimis (OHLCV)
    """
    df = df.copy()
    
    # Pridedame visus indikatorius
    df = add_moving_averages(df)
    df = add_exponential_moving_averages(df)
    df = add_rsi(df)
    df = add_macd(df)
    df = add_bollinger_bands(df)
    df = add_lag_features(df)
    
    # Pridedame target kintamąjį
    df = add_target_label(df)
    
    # Normalizuojame features
    # df = normalize_features(df)  # Komentaras: galite ištrinti jei norite išlaikyti originalius duomenis
    
    # Išvalome eilutes su trūkstamomis reikšmėmis
    df = df.dropna()
    
    return df

if __name__ == "__main__":
    # Šis kodas bus vykdomas tik jei paleisite šį failą tiesiogiai
    print("Techninių indikatorių modulis paleistas tiesiogiai!")
    print("Šis modulis skirtas importavimui į kitus failus.")