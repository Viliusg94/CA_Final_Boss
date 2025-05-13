"""
Pavyzdinis skriptas, demonstruojantis duomenų paruošimo ir transformacijų naudojimą.
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Pridedame pagrindinį projekto katalogą į importavimo kelius
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importuojame duomenų modulius
from data.btc_data import gauti_btc_kainas, paruosti_duomenis
from data.sentiment_analysis import analizuoti_naujienu_sentimenta, prideti_sentimento_duomenis
from database.test_connection import engine, create_database, create_tables, SessionLocal

def parodyti_duomenu_paruosima():
    """
    Demonstruoja duomenų paruošimo ir transformacijų procesą.
    """
    print("=" * 60)
    print("BITCOIN DUOMENŲ PARUOŠIMO IR TRANSFORMACIJŲ PAVYZDYS")
    print("=" * 60)
    
    # 1. Gauname Bitcoin kainas už pastaruosius 6 mėnesius
    print("\n1. Gaunami BTC kainų duomenys už 6 mėnesius...")
    btc_kainos = gauti_btc_kainas(periodas="6mo", intervalas="1d")
    
    if btc_kainos.empty:
        print("❌ Nepavyko gauti BTC kainų duomenų.")
        return
    
    print(f"✅ Gauti {len(btc_kainos)} įrašai.")
    print("\nPirmieji 5 įrašai:")
    print(btc_kainos.head())
    
    # 2. Paruošiame visus duomenis su techniniais rodikliais
    print("\n2. Ruošiami duomenys su visais techniniais rodikliais...")
    pilni_duomenys = paruosti_duomenis(periodas="6mo", intervalas="1d")
    
    if pilni_duomenys.empty:
        print("❌ Nepavyko paruošti duomenų su techniniais rodikliais.")
        return
    
    print(f"✅ Paruošti {len(pilni_duomenys)} įrašai su techniniais rodikliais.")
    print("\nRodiklių sąrašas:")
    print(pilni_duomenys.columns.tolist())
    
    # 3. Patikriname sentimento analizę
    print("\n3. Atliekama Bitcoin naujienų sentimento analizė...")
    sentimento_df = analizuoti_naujienu_sentimenta(max_straipsniu=3)
    
    if sentimento_df.empty:
        print("❌ Nepavyko gauti sentimento duomenų.")
    else:
        print(f"✅ Analizuoti {len(sentimento_df)} straipsniai.")
        print("\nSentimento analizės rezultatai:")
        print(sentimento_df[['title', 'source', 'polarity', 'compound', 'sentiment']])
    
    # 4. Pridedame sentimento duomenis prie kainų
    print("\n4. Pridedami sentimento duomenys prie kainų duomenų...")
    pilni_duomenys_su_sentimentu = prideti_sentimento_duomenis(pilni_duomenys)
    
    if 'Sentiment_Score' not in pilni_duomenys_su_sentimentu.columns:
        print("❌ Nepavyko pridėti sentimento duomenų.")
    else:
        print("✅ Sentimento duomenys sėkmingai pridėti.")
        if not pilni_duomenys_su_sentimentu['Sentiment_Score'].isna().all():
            print(f"Vidutinis sentimento įvertis: {pilni_duomenys_su_sentimentu['Sentiment_Score'].mean():.4f}")
    
    # 5. Išsaugome duomenis
    print("\n5. Išsaugomi pilni duomenys į CSV...")
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "btc_full_data.csv")
    pilni_duomenys_su_sentimentu.to_csv(file_path, index=False)
    print(f"✅ Duomenys išsaugoti į failą: {file_path}")
    
    # 6. Pavaizduojame kelis rodiklius
    print("\n6. Kuriamas vizualizacijos pavyzdys...")
    try:
        plt.figure(figsize=(12, 8))
        
        # Kainos ir slankieji vidurkiai
        plt.subplot(3, 1, 1)
        plt.plot(pilni_duomenys['Date'], pilni_duomenys['Close'], label='BTC kaina')
        plt.plot(pilni_duomenys['Date'], pilni_duomenys['SMA_7'], label='7 dienų SMA')
        plt.plot(pilni_duomenys['Date'], pilni_duomenys['SMA_30'], label='30 dienų SMA')
        plt.title('Bitcoin kaina ir slankieji vidurkiai')
        plt.legend()
        
        # RSI
        plt.subplot(3, 1, 2)
        plt.plot(pilni_duomenys['Date'], pilni_duomenys['RSI_14'], color='purple')
        plt.axhline(y=70, color='r', linestyle='--', alpha=0.3)
        plt.axhline(y=30, color='g', linestyle='--', alpha=0.3)
        plt.title('Santykinis stiprumo indeksas (RSI)')
        plt.ylim(0, 100)
        
        # Apimtis (Volume)
        plt.subplot(3, 1, 3)
        plt.bar(pilni_duomenys['Date'], pilni_duomenys['Volume'], color='blue', alpha=0.6)
        plt.title('Prekybos apimtis (Volume)')
        
        plt.tight_layout()
        
        # Išsaugome paveikslą
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "btc_indicators.png")
        plt.savefig(img_path)
        print(f"✅ Vizualizacija išsaugota į failą: {img_path}")
        
        # Parodome paveikslą
        plt.show()
    
    except Exception as e:
        print(f"❌ Klaida kuriant vizualizaciją: {e}")
    
    print("\nPavyzdys baigtas! 🎉")


def issaugoti_i_db():
    """
    Demonstruoja duomenų išsaugojimą į duomenų bazę.
    """
    print("=" * 60)
    print("BITCOIN DUOMENŲ IŠSAUGOJIMO Į DUOMENŲ BAZĘ PAVYZDYS")
    print("=" * 60)
    
    # 1. Patikriname/sukuriame duomenų bazę
    print("\n1. Tikrinama/kuriama duomenų bazė...")
    if create_database():
        print("✅ Duomenų bazė paruošta.")
    else:
        print("❌ Nepavyko paruošti duomenų bazės.")
        return
    
    # 2. Sukuriame lenteles
    print("\n2. Kuriamos duomenų bazės lentelės...")
    if create_tables():
        print("✅ Lentelės sukurtos.")
    else:
        print("❌ Nepavyko sukurti lentelių.")
        return
    
    # 3. Gauname duomenis
    print("\n3. Gaunami BTC kainų duomenys...")
    btc_kainos = gauti_btc_kainas(periodas="1mo", intervalas="1d")
    
    if btc_kainos.empty:
        print("❌ Nepavyko gauti BTC kainų duomenų.")
        return
    
    print(f"✅ Gauti {len(btc_kainos)} įrašai.")
    
    # 4. Išsaugome duomenis į duomenų bazę
    print("\n4. Išsaugomi duomenys į duomenų bazę...")
    db = SessionLocal()
    
    try:
        # Importuojame BTC kainos modelį
        from database.test_connection import BtcPrice
        
        # Išsaugome duomenis
        skaiciuoklis = 0
        for _, eilute in btc_kainos.iterrows():
            # Tikriname, ar įrašas jau egzistuoja
            existing = db.query(BtcPrice).filter(
                BtcPrice.timestamp == eilute['Date']
            ).first()
            
            # Jei įrašas jau egzistuoja, einame prie kito
            if existing:
                continue
            
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
            db.add(btc_kaina)
            skaiciuoklis += 1
        
        # Įrašome pakeitimus
        db.commit()
        print(f"✅ Sėkmingai išsaugoti {skaiciuoklis} nauji įrašai į duomenų bazę")
        
    except Exception as e:
        # Jei įvyko klaida, atšaukiame pakeitimus
        db.rollback()
        print(f"❌ Klaida išsaugant duomenis į duomenų bazę: {e}")
    
    finally:
        # Uždarome sesiją
        db.close()
    
    print("\nPavyzdys baigtas! 🎉")


if __name__ == "__main__":
    # Demonstruojame duomenų paruošimą
    parodyti_duomenu_paruosima()
    
    print("\n" + "=" * 60)
    
    # Demonstruojame duomenų išsaugojimą į duomenų bazę
    # issaugoti_i_db()  # Užkomentuota, kad nemodifikuotų DB be reikalo
