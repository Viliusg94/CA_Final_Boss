"""
Bitcoin sentimento analizės modulis.
Šis modulis analizuoja Bitcoin sentimentą iš naujienų straipsnių.
Modulis naudoja TextBlob ir NLTK Vader bibliotekas sentimento įvertinimui,
ir surenka informaciją iš populiarių kriptovaliutų naujienų tinklalapių.
"""

# ----- IMPORTAI -----
import requests     # HTTP užklausoms atlikti - gauti duomenis iš tinklalapių
import pandas as pd    # Duomenų apdorojimui ir analizei su DataFrame struktūromis
from datetime import datetime   # Darbui su datomis ir laiku
import logging      # Įvykių registravimui (logging) - sistemos pranešimams
import time         # Laiko operacijoms - uždelsti tarp užklausų
import random       # Atsitiktinumui - atsitiktiniam User-Agent pasirinkimui
from bs4 import BeautifulSoup   # HTML analizei ir duomenų ištraukimui iš tinklalapių
from textblob import TextBlob   # Teksto sentimento analizei
import nltk         # Natūralios kalbos apdorojimo biblioteka

# Atsisiunčiame NLTK duomenis jei reikia
# NLTK Vader reikalauja specialių žodynų analizei, čia tikriname ar jie jau įdiegti
# Jei neįdiegti, juos atsisiunčiame automatiškai - tai būtina sentimento analizei
try:
    nltk.data.find('vader_lexicon')  # Tikriname ar Vader leksikonas jau įdiegtas sistemoje
except LookupError:  # Jei leksikono nėra, atsisiunčiame jį
    nltk.download('vader_lexicon')  # Atsisiunčiame Vader leksikoną, kuriame yra žodžių jausmų įverčiai

# Importuojame SentimentIntensityAnalyzer iš NLTK bibliotekos - šis įrankis leidžia
# atlikti greitą ir tikslų sentimento vertinimą, ypač tinkamą trumpiems tekstams
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Logerio nustatymai - konfigūruojame programos pranešimų sistemą
# Tai padeda sekti programos vykdymą ir geriau suprasti klaidas
logging.basicConfig(
    level=logging.INFO,  # Nurodome pranešimų lygį - INFO reiškia, kad rodysime informacinius pranešimus
    format='%(asctime)s - %(levelname)s - %(message)s',  # Nustatome pranešimų formatą - laikas, lygis, žinutė
    datefmt='%Y-%m-%d %H:%M:%S'  # Datos formatas pranešimuose - metai-mėnuo-diena valanda:minutė:sekundė
)
# Sukuriame specialų logerį šiam moduliui, kad galėtume identifikuoti iš kur ateina pranešimai
logger = logging.getLogger("sentiment_analysis")

# ----- KONSTANTOS -----
# Naujienų šaltiniai - tinklalapių adresai, iš kurių trauksime Bitcoin naujienas
# Šie šaltiniai specializuojasi kriptovaliutų naujienose ir turi specialias Bitcoin kategorijas
NEWS_SOURCES = [
    "https://cointelegraph.com/tags/bitcoin",  # Cointelegraph - vienas didžiausių kriptovaliutų naujienų portalų
    "https://www.coindesk.com/tag/bitcoin/",   # Coindesk - profesionalus kriptovaliutų naujienų šaltinis
    "https://cryptonews.com/news/bitcoin-news/"  # Cryptonews - platus kriptovaliutų naujienų tinklalapis
]

# User-Agent reikšmės - šios antraštės padeda apsimesti tikru naršyklės naudotoju
# Tai padeda išvengti blokavimo, nes daug tinklalapių blokuoja automatinius įrankius
# Kiekviena reikšmė imituoja skirtingą naršyklę ir operacinę sistemą
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",  # Firefox Windows
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"  # Safari Mac
]

# ----- FUNKCIJOS -----
def gauti_atsitiktini_user_agent():
    """
    Grąžina atsitiktinį User-Agent iš sąrašo.
    
    Funkcija padeda apsimesti tikru naršytoju kiekvienai užklausai naudojant
    skirtingą User-Agent reikšmę, taip sumažinant tikimybę būti užblokuotam.
    
    Grąžina:
        str: Atsitiktinė User-Agent reikšmė iš apibrėžto sąrašo
    """
    return random.choice(USER_AGENTS)  # Išrenkame ir grąžiname atsitiktinę reikšmę iš sąrašo

def gauti_duomenis_is_url(url, timeout=10):
    """
    Funkcija gauna duomenis (HTML) iš nurodyto URL adreso.
    
    Siunčia HTTP GET užklausą į nurodytą tinklalapį, naudodama atsitiktinį User-Agent.
    Nustato laiko limitą, kad užklausa neužstrigtų per ilgai.
    
    Parametrai:
        url (str): Tinklalapio URL adresas, iš kurio norime gauti duomenis
        timeout (int): Maksimalus laukimo laikas sekundėmis, kol nutrauks užklausą
    
    Grąžina:
        bytes arba None: Tinklalapio HTML turinys baitų formatu arba None, jei įvyko klaida
    """
    try:
        # Sukuriame antraštę su atsitiktiniu User-Agent, kad tinklalapis manytų, jog esame tikras naršytojas
        headers = {"User-Agent": gauti_atsitiktini_user_agent()}
        
        # Siunčiame GET užklausą į nurodytą URL su mūsų antraštėmis ir laiko limitu
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Tikriname ar užklausa sėkminga (HTTP statusas 200 OK)
        if response.status_code != 200:
            # Jei nesėkminga, užregistruojame įspėjimą ir grąžiname None
            logger.warning(f"Klaida gaunant duomenis iš {url}: {response.status_code}")
            return None
            
        # Jei viskas gerai, grąžiname tinklalapio turinį
        return response.content
    except Exception as e:
        # Įvykus bet kokiai klaidai, užregistruojame ją ir grąžiname None
        logger.error(f"Klaida: {e}")
        return None

def gauti_straipsnius(url, max_straipsniu=10):
    """
    Ištraukia straipsnius iš nurodytos naujienų svetainės.
    
    Funkcija analizuoja tinklalapio HTML ir ištraukia straipsnių antraštes ir nuorodas.
    Pritaikyta trims skirtingoms svetainėms, nes kiekviena turi unikalią HTML struktūrą.
    
    Parametrai:
        url (str): Tinklalapio URL adresas
        max_straipsniu (int): Maksimalus straipsnių skaičius, kurį norime ištraukti
    
    Grąžina:
        list: Straipsnių sąrašas, kur kiekvienas straipsnis yra žodynas su antrašte, URL ir šaltiniu
    """
    # Sukuriame tuščią sąrašą straipsniams
    straipsniai = []
    
    # Gauname tinklalapio turinį
    content = gauti_duomenis_is_url(url)
    
    # Jei turinio negavome, grąžiname tuščią sąrašą
    if not content:
        return []
    
    # Sukuriame BeautifulSoup objektą HTML analizei
    soup = BeautifulSoup(content, 'html.parser')
    
    # Atpažįstame svetainę pagal URL ir taikome atitinkamą duomenų ištraukimo logiką
    if "cointelegraph.com" in url:
        # Cointelegraph straipsnių ištraukimas
        # Ieškome visų 'article' elementų ir pasirenkame tik tiek, kiek nurodyta max_straipsniu
        for article in soup.select('article')[:max_straipsniu]:
            # Ieškome antraštės h2 elemente
            title = article.select_one('h2')
            # Ieškome nuorodos a elemente
            link = article.select_one('a')
            
            # Jei radome ir antraštę, ir nuorodą
            if title and link:
                # Sukuriame straipsnio žodyną ir pridedame į sąrašą
                # Tikriname ar nuoroda pilna, jei ne - pridedame domeno adresą
                straipsniai.append({
                    "title": title.text.strip(),  # Ištraukiame antraštės tekstą ir pašaliname tarpus pradžioje/pabaigoje
                    "url": link.get('href') if link.get('href').startswith('http') else f"https://cointelegraph.com{link.get('href')}",
                    "source": "Cointelegraph"  # Nurodome šaltinį
                })
    elif "coindesk.com" in url:
        # Coindesk straipsnių ištraukimas - logika panaši, tik skiriasi HTML elementų klasės
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
        # Cryptonews straipsnių ištraukimas
        for article in soup.select('.category-posts__post')[:max_straipsniu]:
            title = article.select_one('.category-posts__post-title')
            link = article.select_one('a')
            
            if title and link:
                straipsniai.append({
                    "title": title.text.strip(),
                    "url": link.get('href') if link.get('href').startswith('http') else f"https://cryptonews.com{link.get('href')}",
                    "source": "Cryptonews"
                })
    
    # Grąžiname visus rastus straipsnius
    return straipsniai

def gauti_naujienu_straipsnius(max_straipsniu=10):
    """
    Gauna straipsnius iš visų apibrėžtų šaltinių.
    
    Funkcija aplanko kiekvieną naujienų šaltinį iš NEWS_SOURCES sąrašo
    ir surenka straipsnius, sujungdama juos į vieną didelį sąrašą.
    
    Parametrai:
        max_straipsniu (int): Maksimalus straipsnių skaičius iš kiekvieno šaltinio
    
    Grąžina:
        list: Bendras visų šaltinių straipsnių sąrašas
    """
    # Sukuriame tuščią sąrašą visiems straipsniams
    visi_straipsniai = []
    
    # Einame per visus naujienų šaltinius
    for url in NEWS_SOURCES:
        # Registruojame, kad pradedame ieškoti straipsnių
        logger.info(f"Ieškoma straipsnių: {url}")
        
        # Gauname straipsnius iš šio šaltinio
        straipsniai = gauti_straipsnius(url, max_straipsniu)
        
        # Pridedame rastus straipsnius prie bendro sąrašo
        visi_straipsniai.extend(straipsniai)
        
        # Padarome 1 sekundės pauzę, kad neapkrautume serverio per daug užklausų
        time.sleep(1)
    
    # Registruojame bendrą rastų straipsnių skaičių
    logger.info(f"Rasta straipsnių: {len(visi_straipsniai)}")
    
    # Grąžiname visus rastus straipsnius
    return visi_straipsniai

def gauti_straipsnio_turini(url):
    """
    Gauna straipsnio tekstinį turinį iš nurodyto URL.
    
    Funkcija atsiunčia straipsnio HTML, pašalina skripto ir stiliaus elementus,
    tada ištraukia visą tekstą ir jį išvalo nuo nereikalingų tarpų.
    
    Parametrai:
        url (str): Straipsnio URL adresas
    
    Grąžina:
        str: Išvalytas straipsnio tekstas
    """
    # Gauname straipsnio HTML turinį
    content = gauti_duomenis_is_url(url)
    
    # Jei turinio negavome, grąžiname tuščią tekstą
    if not content:
        return ""
    
    # Sukuriame BeautifulSoup objektą HTML analizei
    soup = BeautifulSoup(content, 'html.parser')
    
    # Pašaliname script ir style elementus, nes juose nėra naudingo teksto
    for script in soup(["script", "style"]):
        script.extract()
    
    # Ištraukiame visą tekstą, naudodami tarpą kaip skyriklį tarp elementų
    text = soup.get_text(separator=' ')
    
    # Išvalome tekstą - pašaliname per daug tarpų ir tuščias eilutes
    # Pirmiausia paimame kiekvieną eilutę ir pašaliname tarpus pradžioje/pabaigoje
    lines = (line.strip() for line in text.splitlines())
    
    # Tada skaidome eilutes į frazes, pašalindami daugybines tarpų sekas
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    
    # Sujungiame visas netuščias frazes į vieną tekstą
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    # Grąžiname išvalytą tekstą
    return text

def analizuoti_sentimenta(tekstas):
    """
    Analizuoja teksto sentimentą naudojant TextBlob ir NLTK Vader.
    
    Ši funkcija atlieka dvigubą sentimento analizę - naudoja ir TextBlob, ir NLTK Vader.
    TextBlob nustato polarity (teigiamumas/neigiamumas) ir subjectivity (subjektyvumas),
    o NLTK Vader pateikia detalesnę analizę su compound, neg, neu ir pos reikšmėmis.
    
    Parametrai:
        tekstas (str): Tekstas, kurį reikia analizuoti
    
    Grąžina:
        dict: Žodynas su įvairiais sentimento įverčiais
    """
    try:
        # TextBlob analizė
        blob = TextBlob(tekstas)
        # Polarity: nuo -1 (labai neigiamas) iki 1 (labai teigiamas)
        polarity = blob.sentiment.polarity
        # Subjectivity: nuo 0 (labai objektyvus) iki 1 (labai subjektyvus)
        subjectivity = blob.sentiment.subjectivity
        
        # NLTK Vader analizė - specializuota socialinių tinklų tekstų analizei
        sia = SentimentIntensityAnalyzer()
        # Gauna įverčius: compound (bendras), neg (neigiamas), neu (neutralus), pos (teigiamas)
        vader_scores = sia.polarity_scores(tekstas)
        
        # Grąžiname visus sentimento rodiklius viename žodyne
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "compound": vader_scores["compound"],  # Bendras įvertis nuo -1 iki 1
            "neg": vader_scores["neg"],  # Neigiamo sentimento dalis (0-1)
            "neu": vader_scores["neu"],  # Neutralaus sentimento dalis (0-1)
            "pos": vader_scores["pos"]   # Teigiamo sentimento dalis (0-1)
        }
    except Exception as e:
        # Įvykus klaidai, užregistruojame ją ir grąžiname nulines reikšmes
        logger.error(f"Klaida analizuojant sentimentą: {e}")
        return {"polarity": 0, "subjectivity": 0, "compound": 0, "neg": 0, "neu": 0, "pos": 0}

def analizuoti_naujienu_sentimenta(max_straipsniu=5):
    """
    Analizuoja naujienų straipsnių sentimentą.
    
    Ši funkcija atlieka visą darbą - gauna straipsnius, ištraukia jų turinį,
    analizuoja sentimentą ir grąžina rezultatus kaip pandas DataFrame.
    
    Parametrai:
        max_straipsniu (int): Maksimalus straipsnių skaičius iš kiekvieno šaltinio
    
    Grąžina:
        pandas.DataFrame: Straipsnių ir jų sentimento duomenų lentelė
    """
    # Gauname straipsnius iš visų šaltinių
    straipsniai = gauti_naujienu_straipsnius(max_straipsniu)
    
    # Jei negavome jokių straipsnių, užregistruojame įspėjimą ir grąžiname tuščią DataFrame
    if not straipsniai:
        logger.warning("Nerasta straipsnių analizei")
        return pd.DataFrame()
    
    # Sukuriame tuščią sąrašą rezultatams
    rezultatai = []
    
    # Analizuojame kiekvieną straipsnį
    for straipsnis in straipsniai:
        # Gauname straipsnio pilną tekstinį turinį
        turinys = gauti_straipsnio_turini(straipsnis["url"])
        
        # Jei nepavyko gauti turinio, naudojame antraštę
        if not turinys:
            turinys = straipsnis["title"]
        
        # Analizuojame straipsnio sentimentą
        sentimentas = analizuoti_sentimenta(turinys)
        
        # Nustatome sentimento kategoriją pagal compound reikšmę
        # > 0.05 laikome teigiamu, < -0.05 laikome neigiamu, kitu atveju - neutraliu
        if sentimentas["compound"] > 0.05:
            sentiment_category = "positive"
        elif sentimentas["compound"] < -0.05:
            sentiment_category = "negative"
        else:
            sentiment_category = "neutral"
        
        # Pridedame rezultatą į sąrašą
        rezultatai.append({
            "title": straipsnis["title"],  # Straipsnio antraštė
            "source": straipsnis["source"],  # Šaltinis (svetainė)
            "url": straipsnis["url"],  # Straipsnio URL
            "date": datetime.now().strftime("%Y-%m-%d"),  # Dabartinė data
            "polarity": sentimentas["polarity"],  # TextBlob polarity
            "subjectivity": sentimentas["subjectivity"],  # TextBlob subjectivity
            "compound": sentimentas["compound"],  # Vader compound įvertis
            "sentiment": sentiment_category  # Sentimento kategorija
        })
        
        # Padarome 1 sekundės pauzę, kad neapkrautume serverio
        time.sleep(1)
    
    # Sukuriame pandas DataFrame iš rezultatų sąrašo
    df = pd.DataFrame(rezultatai)
    
    # Apskaičiuojame vidutinį sentimentą (compound reikšmę)
    vidutinis_sentimentas = df["compound"].mean() if not df.empty else 0
    logger.info(f"Vidutinis sentimentas: {vidutinis_sentimentas:.2f} ({len(df)} straipsniai)")
    
    # Grąžiname DataFrame su rezultatais
    return df

def prideti_sentimento_duomenis(kainu_df):
    """
    Prideda sentimento duomenis prie kainų DataFrame.
    
    Ši funkcija priima Bitcoin kainų DataFrame ir prideda prie jo
    sentimento rodiklius, sujungdama duomenis pagal datą.
    
    Parametrai:
        kainu_df (pandas.DataFrame): Bitcoin kainų duomenys
    
    Grąžina:
        pandas.DataFrame: Kainų duomenys papildyti sentimento rodikliais
    """
    try:
        # Kopijuojame duomenis, kad nepakeistume originalo
        df = kainu_df.copy()
        
        # Tikriname ar yra Date stulpelis - jis būtinas sujungimui
        if 'Date' not in df.columns:
            logger.error("Nėra 'Date' stulpelio - negalima pridėti sentimento duomenų.")
            return kainu_df  # Grąžiname originalą, jei negalime atlikti sujungimo
        
        # Gauname sentimento duomenis
        sentimento_df = analizuoti_naujienu_sentimenta(max_straipsniu=10)
        
        # Jei negavome sentimento duomenų, pridedame tuščius stulpelius
        if sentimento_df.empty:
            df['Sentiment_Score'] = float('nan')  # NaN reikšmė - nėra duomenų
            df['Sentiment_TextBlob'] = float('nan')
            logger.warning("Nėra sentimento duomenų, pridėti tušti stulpeliai.")
            return df
        
        # Konvertuojame datas į pandas datetime formatą, kad galėtume sujungti
        sentimento_df['date'] = pd.to_datetime(sentimento_df['date'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Grupuojame sentimento duomenis pagal datą ir skaičiuojame vidurkius
        # Tai reikalinga, nes vienai dienai gali būti keli straipsniai
        sentimento_agg = sentimento_df.groupby('date').agg({
            'compound': 'mean',  # Sentimento compound įverčių vidurkis
            'polarity': 'mean'   # TextBlob polarity įverčių vidurkis
        }).reset_index().rename(columns={
            'compound': 'Sentiment_Score',  # Pervardijame stulpelius
            'polarity': 'Sentiment_TextBlob'
        })
        
        # Sujungiame kainų ir sentimento duomenis pagal datą
        # 'left' reiškia, kad išsaugosime visus kainų įrašus, net jei nėra sentimento duomenų
        df = pd.merge(df, sentimento_agg, left_on='Date', right_on='date', how='left')
        
        # Pašaliname dubliuotą 'date' stulpelį
        if 'date' in df.columns:
            df = df.drop('date', axis=1)
        
        # Užpildome trūkstamas reikšmes - forward fill, po to backward fill
        # Tai reiškia, kad tuščioms dienoms naudosime artimiausios ankstesnės,
        # o jei tokios nėra - artimiausios vėlesnės dienos reikšmes
        df['Sentiment_Score'] = df['Sentiment_Score'].fillna(method='ffill').fillna(method='bfill')
        df['Sentiment_TextBlob'] = df['Sentiment_TextBlob'].fillna(method='ffill').fillna(method='bfill')
        
        # Apskaičiuojame 7 dienų slankųjį vidurkį sentimento įverčiams
        # Tai padeda išlyginti didelius svyravimus ir matyti bendrą tendenciją
        df['Sentiment_Score_SMA7'] = df['Sentiment_Score'].rolling(window=7).mean()
        
        logger.info("Sėkmingai pridėti sentimento duomenys")
        return df
    
    except Exception as e:
        # Įvykus klaidai, užregistruojame ją ir grąžiname originalius duomenis
        logger.error(f"Klaida pridedant sentimento duomenis: {e}")
        return kainu_df

# Jei failas vykdomas tiesiogiai (ne importuojamas kaip modulis)
if __name__ == "__main__":
    # Analizuojame sentimentą - gauname pagrindinius sentimento duomenis
    sentimento_df = analizuoti_naujienu_sentimenta(max_straipsniu=5)
    
    # Rodome ir saugome rezultatus
    if not sentimento_df.empty:
        # Rodome tik pagrindinius stulpelius konsolėje (ne visą DataFrame)
        print(sentimento_df[['title', 'source', 'polarity', 'compound', 'sentiment']])
        
        # Išsaugome pilnus rezultatus į CSV failą - lengvai peržiūrimą formato
        sentimento_df.to_csv("bitcoin_sentiment.csv", index=False)
        print(f"Duomenys išsaugoti: bitcoin_sentiment.csv")
    else:
        # Jei nepavyko gauti duomenų, išvedame klaidos pranešimą
        print("Nepavyko gauti sentimento duomenų.")