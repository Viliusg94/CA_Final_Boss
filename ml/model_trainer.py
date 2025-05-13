"""
Mašininio mokymosi modelio treniravimo modulis su SQLAlchemy ORM
"""
import os
import sys
import logging
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Šis kelias leidžia importuoti modulius iš kitų direktorijų
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Importuojame duomenų bazės prisijungimą
from database.config import SessionLocal
# Importuojame duomenų bazės modelius
from database.models import BtcFeatures, MLModel

# Sukuriame modelių katalogą, jei jo nėra
os.makedirs('models', exist_ok=True)

# Logeris
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("model_trainer")

def get_training_data():
    """
    Gauna treniravimo duomenis naudojant SQLAlchemy ORM
    
    Grąžina:
        DataFrame su feature ir target stulpeliais
    """
    try:
        # Sukuriame sesiją
        session = SessionLocal()
        
        # Gauname duomenis per ORM užklausą
        features = session.query(BtcFeatures).order_by(BtcFeatures.timestamp).all()
        
        # Konvertuojame ORM objektus į DataFrame
        data = []
        for feature in features:
            # Kiekvienas feature yra BtcFeatures objektas, kurį konvertuojame į žodyną
            record = {
                'timestamp': feature.timestamp,
                'open': feature.open,
                'high': feature.high,
                'low': feature.low,
                'close': feature.close,
                'volume': feature.volume,
                
                # SMA
                'sma_5': feature.sma_5,
                'sma_10': feature.sma_10,
                'sma_20': feature.sma_20,
                'sma_50': feature.sma_50,
                'sma_200': feature.sma_200,
                
                # EMA
                'ema_5': feature.ema_5,
                'ema_10': feature.ema_10,
                'ema_20': feature.ema_20,
                'ema_50': feature.ema_50,
                'ema_200': feature.ema_200,
                
                # RSI
                'rsi_14': feature.rsi_14,
                
                # MACD
                'macd': feature.macd,
                'macd_signal': feature.macd_signal,
                'macd_histogram': feature.macd_histogram,
                
                # Bollinger
                'bb_middle': feature.bb_middle,
                'bb_upper': feature.bb_upper,
                'bb_lower': feature.bb_lower,
                'bb_width': feature.bb_width,
                
                # Lag features
                'close_lag_1': feature.close_lag_1,
                'close_lag_2': feature.close_lag_2,
                'close_lag_3': feature.close_lag_3,
                'close_lag_5': feature.close_lag_5,
                'close_lag_7': feature.close_lag_7,
                'close_lag_14': feature.close_lag_14,
                'close_lag_21': feature.close_lag_21,
                
                'return_lag_1': feature.return_lag_1,
                'return_lag_2': feature.return_lag_2,
                'return_lag_3': feature.return_lag_3,
                'return_lag_5': feature.return_lag_5,
                'return_lag_7': feature.return_lag_7,
                'return_lag_14': feature.return_lag_14,
                'return_lag_21': feature.return_lag_21,
                
                # Target
                'target': feature.target
            }
            
            data.append(record)
        
        # Sukuriame DataFrame
        df = pd.DataFrame(data)
        
        # Uždarome sesiją
        session.close()
        
        logger.info(f"Iš DB gauta {len(df)} eilučių treniravimui")
        return df
    except Exception as e:
        logger.error(f"Klaida gaunant duomenis: {e}")
        # Uždarome sesiją, jei ji buvo sukurta
        if 'session' in locals():
            session.close()
        return pd.DataFrame()

def save_model_to_db(model_name, accuracy, precision, recall, f1, model_path):
    """
    Išsaugo modelio metrikas į duomenų bazę per SQLAlchemy ORM
    
    Parametrai:
        model_name: Modelio pavadinimas
        accuracy: Tikslumas
        precision: Preciziškumas
        recall: Jautrumas
        f1: F1 rezultatas
        model_path: Kelias iki išsaugoto modelio
    """
    try:
        # Sukuriame sesiją
        session = SessionLocal()
        
        # Sukuriame naują modelio įrašą
        ml_model = MLModel(
            name=model_name,
            created_at=datetime.now(),
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            model_path=model_path
        )
        
        # Pridedame ir išsaugome
        session.add(ml_model)
        session.commit()
        
        logger.info(f"Modelis {model_name} išsaugotas į DB")
        session.close()
        return True
    except Exception as e:
        logger.error(f"Klaida išsaugant modelį į DB: {e}")
        # Atšaukiame pakeitimus jei buvo klaida
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

def train_model():
    """
    Apmoko mašininio mokymosi modelį ir išsaugo į DB
    
    Grąžina:
        bool: True jei pavyko, False jei nepavyko
    """
    try:
        # Gauname duomenis
        df = get_training_data()
        
        if df.empty:
            logger.error("Nepavyko gauti duomenų treniravimui")
            return False
        
        # Pašaliname eilutes su trūkstamomis reikšmėmis
        df = df.dropna()
        
        # Pašaliname timestamp stulpelį (netinka modelio treniravimui)
        X = df.drop(['timestamp', 'target'], axis=1)
        y = df['target']
        
        # Padalijame duomenis į treniravimo ir testavimo rinkinius
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        logger.info(f"Treniravimo duomenų dydis: {X_train.shape}")
        logger.info(f"Testavimo duomenų dydis: {X_test.shape}")
        
        # Sukuriame ir apmokome modelį
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Testuojame modelį
        y_pred = model.predict(X_test)
        
        # Skaičiuojame metrikai
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        logger.info(f"Modelio tikslumas: {acc:.4f}")
        logger.info(f"Modelio preciziškumas: {prec:.4f}")
        logger.info(f"Modelio jautrumas: {rec:.4f}")
        logger.info(f"Modelio F1 rezultatas: {f1:.4f}")
        
        # Išsaugome modelį į failą
        model_name = f"btc_predictor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"models/{model_name}.joblib"
        joblib.dump(model, model_path)
        logger.info(f"Modelis išsaugotas į {model_path}")
        
        # Išsaugome modelį į DB
        save_model_to_db(model_name, acc, prec, rec, f1, model_path)
        
        return True
    except Exception as e:
        logger.error(f"Klaida treniruojant modelį: {e}")
        return False

if __name__ == "__main__":
    logger.info("===== Pradedamas modelio treniravimas =====")
    train_model()