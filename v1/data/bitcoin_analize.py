"""
Bitcoin duomenų analizės modulis.
Šis modulis gauna ir analizuoja Bitcoin kainas ir sentimento duomenis.
"""

# ----- IMPORTAI -----
# Kainų duomenų gavimui ir analizei
import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

# Sentimento analizei ir duomenų gavimui iš tinklalapių
import requests
import time
import random
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk

# Kitos bibliotekos
from datetime import datetime
import logging

# Atsisiunčiame reikalingus NLTK duomenis
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Sentimento analizei
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Logerio nustatymai
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("bitcoin_analize")

# ----- KONSTANTOS -----
# Kainų duomenų gavimui
BTC_SYMBOL = "BTC-USD"
DEFAULT_PERIOD = "2y"
DEFAULT_INTERVAL = "1d"

# Sentimento analizei
NEWS_SOURCES = [
    "https://cointelegraph.com/tags/bitcoin",
    "https://www.coindesk.com/tag/bitcoin/",
    "https://cryptonews.com/news/bitcoin-news/"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]

# ----- KAINŲ DUOMENŲ GAVIMO IR ANALIZĖS FUNKCIJOS -----

def gauti_btc_kainas(pradzia=None, pabaiga=None, periodas=DEFAULT_PERIOD, intervalas=DEFAULT_INTERVAL):
    """Gauna Bitcoin kainas iš Yahoo Finance API"""
    try:
        logger.info("Gaunami BTC kainų duomenys")
        
        # Gauname duomenis
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
        if 'Datetime' in duomenys.columns:
            duomenys = duomenys.rename(columns={'Datetime': 'Date'})
        
        logger.info(f"Gauti {len(duomenys)} BTC kainų įrašai")
        return duomenys
    except Exception as e:
        logger.error(f"Klaida gaunant BTC duomenis: {e}")
        return pd.DataFrame()

def prideti_rodiklius(duomenys):
    """Prideda visus techninius rodiklius prie kainų duomenų"""
    try:
        df = duomenys.copy()
        
        # Tikriname ar yra reikalingi stulpeliai
        if 'Close' not in df.columns:
            logger.error("Duomenyse nėra 'Close' stulpelio")
            return duomenys
        
        # 1. Slankieji vidurkiai
        for periodas in [1, 7, 30, 90]:
            df[f'SMA_{periodas}'] = SMAIndicator(close=df['Close'], window=periodas).sma_indicator()
        
        for periodas in [7, 30]:
            df[f'EMA_{periodas}'] = EMAIndicator(close=df['Close'], window=periodas).ema_indicator()
        
        # 2. RSI
        df['RSI_14'] = RSIIndicator(close=df['Close'], window=14).rsi()
        
        # 3. MACD
        macd = MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Histogram'] = macd.macd_diff()
        
        # 4. Bollinger juostos
        bollinger = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Mid'] = bollinger.bollinger_mavg()
        df['BB_Low'] = bollinger.bollinger_lband()
        
        # 5. Kainų pokyčiai
        if 'Volume' in df.columns:
            df['Price_Change'] = df['Close'].diff()
            df['Price_Change_Pct'] = df['Close'].pct_change() * 100
            df['Return_7d'] = df['Close'].pct_change(periods=7) * 100
            df['Return_30d'] = df['Close'].pct_change(periods=30) * 100
            df['Volatility_30d'] = df['Price_Change_Pct'].rolling(window=30).std()
            df['Volume_Change'] = df['Volume'].pct_change() * 100
            df['Volume_SMA_7'] = df['Volume'].rolling(window=7).mean()
        
        logger.info("Pridėti techniniai rodikliai ir pokyčiai")
        return df
    
    except Exception as e:
        logger.error(f"Klaida pridedant rodiklius: {e}")
        return duomenys

def paruosti_duomenis(pradzia=None, pabaiga=None, periodas=DEFAULT_PERIOD, intervalas=DEFAULT_INTERVAL):
    """Paruošia BTC duomenis su visais rodikliais"""
    # Gauname kainas
    df = gauti_btc_kainas(pradzia, pabaiga, periodas, intervalas)
    
    if df.empty:
        return df
    
    # Pridedame rodiklius
    df = prideti_rodiklius(df)
    
    # Pašaliname trūkstamas reikšmes
    df = df.dropna()
    
    logger.info(f"Sėkmingai paruošti {len(df)} įrašai")
    return df

# ----- SENTIMENTO ANALIZĖS FUNKCIJOS -----

def gauti_atsitiktini_user_agent():
    """Grąžina atsitiktinį User-Agent"""
    return random.choice(USER_AGENTS)

def gauti_duomenis_is_url(url, timeout=10):
    """Gauna HTML duomenis iš nurodyto URL"""
    try:
        headers = {"User-Agent": gauti_atsitiktini_user_agent()}
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code != 200:
            logger.warning(f"Klaida gaunant duomenis iš {url}: {response.status_code}")
            return None
            
        return response.content
    except Exception as e:
        logger.error(f"Klaida: {e}")
        return None

def gauti_straipsnius(url, max_straipsniu=10):
    """Ištraukia straipsnius iš naujienų svetainės"""
    straipsniai = []
    content = gauti_duomenis_is_url(url)
    
    if not content:
        return []
        
    soup = BeautifulSoup(content, 'html.parser')
    
    # Skirtinga logika skirtingoms svetainėms
    if "cointelegraph.com" in url:
        for article in soup.select('article')[:max_straipsniu]:
            title = article.select_one('h2')
            link = article.select_one('a')
            if title and link:
                straipsniai.append({
                    "title": title.text.strip(),
                    "url": link.get('href') if link.get('href').startswith('http') else f"https://cointelegraph.com{link.get('href')}",
                    "source": "Cointelegraph"
                })
    elif "coindesk.com" in url:
        for article in soup.select('.article-card')[:max_straipsniu]:
            title = article.select_one('.article-card-title')
            link = article.select_one('a')
            if title and link:
                straipsniai.append({
                    "title": title.text.strip(),
                    "url": link.get('href') if link.get('href').startswith('http') else f"https://www.coindesk.com{link.get('href')}",
                    "source": "Coindesk"
                })
    elif "cryptonews.com" in url:
        for article in soup.select('.category-posts__post')[:max_straipsniu]:
            title = article.select_one('.category-posts__post-title')
            link = article.select_one('a')
            if title and link:
                straipsniai.append({
                    "title": title.text.strip(),
                    "url": link.get('href') if link.get('href').startswith('http') else f"https://cryptonews.com{link.get('href')}",
                    "source": "Cryptonews"
                })
                
    return straipsniai

def gauti_naujienu_straipsnius(max_straipsniu=10):
    """Gauna straipsnius iš visų šaltinių"""
    visi_straipsniai = []
    
    for url in NEWS_SOURCES:
        logger.info(f"Ieškoma straipsnių: {url}")
        straipsniai = gauti_straipsnius(url, max_straipsniu)
        visi_straipsniai.extend(straipsniai)
        time.sleep(1)  # Pauzė tarp užklausų
        
    logger.info(f"Rasta straipsnių: {len(visi_straipsniai)}")
    return visi_straipsniai

def gauti_straipsnio_turini(url):
    """Gauna straipsnio tekstinį turinį"""
    content = gauti_duomenis_is_url(url)
    
    if not content:
        return ""
        
    soup = BeautifulSoup(content, 'html.parser')
    
    # Pašaliname nereikalingus elementus
    for script in soup(["script", "style"]):
        script.extract()
    
    # Gauname tekstą
    text = soup.get_text(separator=' ')
    
    # Išvalome tekstą
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def analizuoti_sentimenta(tekstas):
    """Analizuoja teksto sentimentą"""
    try:
        # TextBlob analizė
        blob = TextBlob(tekstas)
        polarity = blob.sentiment.polarity      # Nuo -1 (neigiamas) iki 1 (teigiamas)
        subjectivity = blob.sentiment.subjectivity  # Nuo 0 (objektyvus) iki 1 (subjektyvus)
        
        # NLTK Vader analizė
        sia = SentimentIntensityAnalyzer()
        vader_scores = sia.polarity_scores(tekstas)
        
        # Rezultatai
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "compound": vader_scores["compound"],
            "neg": vader_scores["neg"],
            "neu": vader_scores["neu"],
            "pos": vader_scores["pos"]
        }
    except Exception as e:
        logger.error(f"Klaida analizuojant sentimentą: {e}")
        return {"polarity": 0, "subjectivity": 0, "compound": 0, "neg": 0, "neu": 0, "pos": 0}

def analizuoti_naujienu_sentimenta(max_straipsniu=5):
    """Analizuoja naujienų straipsnių sentimentą"""
    # Gauname straipsnius
    straipsniai = gauti_naujienu_straipsnius(max_straipsniu)
    
    if not straipsniai:
        logger.warning("Nerasta straipsnių analizei")
        return pd.DataFrame()
    
    rezultatai = []
    
    # Analizuojame kiekvieną straipsnį
    for straipsnis in straipsniai:
        # Gauname turinį
        turinys = gauti_straipsnio_turini(straipsnis["url"])
        
        if not turinys:
            turinys = straipsnis["title"]  # Jei nepavyko gauti turinio, naudojame antraštę
        
        # Analizuojame
        sentimentas = analizuoti_sentimenta(turinys)
        
        # Nustatome sentimento kategoriją
        if sentimentas["compound"] > 0.05:
            sentiment_category = "positive"
        elif sentimentas["compound"] < -0.05:
            sentiment_category = "negative"
        else:
            sentiment_category = "neutral"
        
        # Pridedame rezultatą
        rezultatai.append({
            "title": straipsnis["title"],
            "source": straipsnis["source"],
            "url": straipsnis["url"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "polarity": sentimentas["polarity"],
            "subjectivity": sentimentas["subjectivity"],
            "compound": sentimentas["compound"],
            "sentiment": sentiment_category
        })
        
        time.sleep(1)  # Pauzė
    
    # Sukuriame DataFrame
    df = pd.DataFrame(rezultatai)
    
    # Apskaičiuojame vidutinį sentimentą
    vidutinis_sentimentas = df["compound"].mean() if not df.empty else 0
    logger.info(f"Vidutinis sentimentas: {vidutinis_sentimentas:.2f} ({len(df)} straipsniai)")
    
    return df

def prideti_sentimento_duomenis(kainu_df):
    """Prideda sentimento duomenis prie kainų DataFrame"""
    try:
        df = kainu_df.copy()
        
        # Tikriname ar yra Date stulpelis
        if 'Date' not in df.columns:
            logger.error("Nėra 'Date' stulpelio - negalima pridėti sentimento duomenų")
            return kainu_df
        
        # Gauname sentimento duomenis
        sentimento_df = analizuoti_naujienu_sentimenta(max_straipsniu=10)
        
        if sentimento_df.empty:
            # Pridedame tuščius stulpelius
            df['Sentiment_Score'] = float('nan')
            df['Sentiment_TextBlob'] = float('nan')
            logger.warning("Nėra sentimento duomenų, pridėti tušti stulpeliai")
            return df
        
        # Konvertuojame datas
        sentimento_df['date'] = pd.to_datetime(sentimento_df['date'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Grupuojame duomenis
        sentimento_agg = sentimento_df.groupby('date').agg({
            'compound': 'mean',
            'polarity': 'mean'
        }).reset_index().rename(columns={
            'compound': 'Sentiment_Score',
            'polarity': 'Sentiment_TextBlob'
        })
        
        # Sujungiame duomenis
        df = pd.merge(df, sentimento_agg, left_on='Date', right_on='date', how='left')
        if 'date' in df.columns:
            df = df.drop('date', axis=1)
        
        # Užpildome trūkstamas reikšmes
        df['Sentiment_Score'] = df['Sentiment_Score'].fillna(method='ffill').fillna(method='bfill')
        df['Sentiment_TextBlob'] = df['Sentiment_TextBlob'].fillna(method='ffill').fillna(method='bfill')
        
        # Slankusis vidurkis
        df['Sentiment_Score_SMA7'] = df['Sentiment_Score'].rolling(window=7).mean()
        
        logger.info("Sėkmingai pridėti sentimento duomenys")
        return df
    
    except Exception as e:
        logger.error(f"Klaida pridedant sentimento duomenis: {e}")
        return kainu_df

# ----- PAGRINDINĖS FUNKCIJOS -----

def gauti_pilnus_btc_duomenis(periodas=DEFAULT_PERIOD, prideti_sentimenta=True):
    """
    Pagrindinė funkcija gauti Bitcoin duomenis su technine ir sentimento analize
    
    Parametrai:
        periodas (str): Duomenų periodas ("1d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        prideti_sentimenta (bool): Ar pridėti sentimento duomenis
    
    Grąžina:
        pandas.DataFrame: Bitcoin duomenys su visais rodikliais
    """
    # Gauname kainas su rodikliais
    df = paruosti_duomenis(periodas=periodas)
    
    if df.empty:
        logger.error("Nepavyko gauti Bitcoin kainų duomenų")
        return df
    
    # Pridedame sentimento duomenis jei reikia
    if prideti_sentimenta:
        df = prideti_sentimento_duomenis(df)
    
    return df

def issaugoti_i_duombaze(duomenys, db_session):
    """Išsaugo duomenis į duomenų bazę"""
    try:
        from database.models import BtcPrice
        
        įrašų_skaičius = 0
        
        for _, eilute in duomenys.iterrows():
            btc_kaina = BtcPrice(
                timestamp=eilute['Date'],
                open=eilute['Open'],
                high=eilute['High'],
                low=eilute['Low'],
                close=eilute['Close'],
                volume=eilute['Volume']
            )
            
            db_session.add(btc_kaina)
            įrašų_skaičius += 1
        
        db_session.commit()
        logger.info(f"Išsaugoti {įrašų_skaičius} įrašai į DB")
        return True
    
    except Exception as e:
        if 'db_session' in locals():
            db_session.rollback()
        logger.error(f"Klaida išsaugant į DB: {e}")
        return False

# Jei failas vykdomas tiesiogiai
if __name__ == "__main__":
    print("Bitcoin analizės įrankis")
    print("------------------------")
    
    # Pirmiausia rodome kainas
    print("\n1. GAUNAMI BITCOIN KAINŲ DUOMENYS...")
    btc_duomenys = gauti_btc_kainas(periodas="1mo")
    if not btc_duomenys.empty:
        print(f"Gauti {len(btc_duomenys)} įrašai")
        print(btc_duomenys.head(3))
    else:
        print("Nepavyko gauti kainų duomenų")
    
    # Tada gauname sentimento duomenis
    print("\n2. ANALIZUOJAMAS BITCOIN SENTIMENTAS...")
    sentimento_df = analizuoti_naujienu_sentimenta(max_straipsniu=3)
    if not sentimento_df.empty:
        print(f"Išanalizuoti {len(sentimento_df)} straipsniai")
        print(sentimento_df[['title', 'source', 'compound', 'sentiment']])
    else:
        print("Nepavyko gauti sentimento duomenų")
    
    # Galutinė analizė
    print("\n3. ATLIEKAMA PILNA BITCOIN ANALIZĖ...")
    pilni_duomenys = gauti_pilnus_btc_duomenis(periodas="1mo")
    if not pilni_duomenys.empty:
        print(f"Pilni duomenys su {pilni_duomenys.shape[1]} rodikliais")
        # Išsaugome CSV
        csv_failas = "bitcoin_analize.csv"
        pilni_duomenys.to_csv(csv_failas, index=False)
        print(f"Duomenys išsaugoti: {csv_failas}")
    else:
        print("Nepavyko atlikti pilnos analizės")
