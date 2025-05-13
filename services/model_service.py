"""
Modelio treniravimo ir prognozavimo paslaugos
"""
import os
import sys
import logging
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Pridedame projekto direktoriją į kelią
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import SessionLocal
from database.models import BtcFeatures, MLModel

# Sukuriame modelių katalogą, jei jo nėra
os.makedirs('models', exist_ok=True)

logger = logging.getLogger(__name__)

def get_training_data():
    """
    Gauna treniravimo duomenis naudojant SQLAlchemy ORM
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
                
                # Techniniai indikatoriai
                'sma_5': feature.sma_5,
                'sma_20': feature.sma_20,
                'sma_50': feature.sma_50,
                'ema_5': feature.ema_5,
                'ema_20': feature.ema_20,
                'ema_50': feature.ema_50,
                'rsi_14': feature.rsi_14,
                'macd': feature.macd,
                'macd_signal': feature.macd_signal,
                'macd_histogram': feature.macd_histogram,
                'bb_middle': feature.bb_middle,
                'bb_upper': feature.bb_upper,
                'bb_lower': feature.bb_lower,
                'bb_width': feature.bb_width,
                
                # Lag features
                'close_lag_1': feature.close_lag_1,
                'close_lag_2': feature.close_lag_2,
                'close_lag_3': feature.close_lag_3,
                'return_lag_1': feature.return_lag_1,
                'return_lag_2': feature.return_lag_2,
                'return_lag_3': feature.return_lag_3,
                
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
        
        # Gauname modelio ID
        model_id = ml_model.id
        
        logger.info(f"Modelis {model_name} išsaugotas į DB su ID {model_id}")
        session.close()
        return model_id
    except Exception as e:
        logger.error(f"Klaida išsaugant modelį į DB: {e}")
        # Atšaukiame pakeitimus jei buvo klaida
        if 'session' in locals():
            session.rollback()
            session.close()
        return None

def create_model(model_type, params):
    """
    Sukuria modelį pagal nurodytą tipą ir parametrus
    """
    if model_type == 'random_forest':
        return RandomForestClassifier(
            n_estimators=params.get('n_estimators', 100),
            max_depth=params.get('max_depth', None),
            random_state=42
        )
    elif model_type == 'gradient_boosting':
        return GradientBoostingClassifier(
            learning_rate=params.get('learning_rate', 0.1),
            n_estimators=params.get('n_estimators', 100),
            random_state=42
        )
    elif model_type == 'svm':
        return SVC(
            C=params.get('C', 1.0),
            probability=True,
            random_state=42
        )
    else:
        raise ValueError(f"Nežinomas modelio tipas: {model_type}")

def train_model_with_params(model_type, test_size, params):
    """
    Treniruoja modelį su nurodytais parametrais
    """
    try:
        # Gauname duomenis
        df = get_training_data()
        
        if df.empty:
            raise ValueError("Nepavyko gauti duomenų treniravimui")
        
        # Pašaliname eilutes su trūkstamomis reikšmėmis
        df = df.dropna()
        
        # Pašaliname timestamp stulpelį (netinka modelio treniravimui)
        X = df.drop(['timestamp', 'target'], axis=1)
        y = df['target']
        
        # Padalijame duomenis į treniravimo ir testavimo rinkinius
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        
        logger.info(f"Treniravimo duomenų dydis: {X_train.shape}")
        logger.info(f"Testavimo duomenų dydis: {X_test.shape}")
        
        # Sukuriame ir apmokome modelį
        model = create_model(model_type, params)
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
        model_name = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = f"models/{model_name}.joblib"
        joblib.dump(model, model_path)
        logger.info(f"Modelis išsaugotas į {model_path}")
        
        # Išsaugome modelį į DB
        model_id = save_model_to_db(model_name, acc, prec, rec, f1, model_path)
        
        # Gauname požymių svarbą (tik jei modelis palaiko feature_importances_)
        feature_importance = None
        feature_names = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = model.feature_importances_.tolist()
            feature_names = X.columns.tolist()
            
            # Išrūšiuojame pagal svarbą
            importance_data = sorted(zip(feature_names, feature_importance), key=lambda x: x[1], reverse=True)
            feature_names = [x[0] for x in importance_data[:10]]  # Top 10
            feature_importance = [x[1] for x in importance_data[:10]]
        
        return {
            'model_id': model_id,
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'feature_importance': feature_importance,
            'feature_names': feature_names
        }
    except Exception as e:
        logger.error(f"Klaida treniruojant modelį: {e}")
        return {
            'error': str(e)
        }

def load_model(model_id):
    """
    Įkelia modelį iš disko pagal ID
    """
    try:
        # Gauname modelio informaciją iš DB
        session = SessionLocal()
        model_info = session.query(MLModel).filter(MLModel.id == model_id).first()
        session.close()
        
        if not model_info:
            raise ValueError(f"Modelis su ID {model_id} nerastas")
        
        # Įkeliame modelį iš disko
        model_path = model_info.model_path
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelio failas nerastas: {model_path}")
        
        model = joblib.load(model_path)
        return model, model_info
    except Exception as e:
        logger.error(f"Klaida įkeliant modelį: {e}")
        return None, None

def get_latest_data(days=30):
    """
    Gauna paskutinių dienų duomenis
    """
    try:
        session = SessionLocal()
        
        # Gauname paskutines N dienų duomenis
        features = (session.query(BtcFeatures)
                   .order_by(BtcFeatures.timestamp.desc())
                   .limit(days)
                   .all())
        
        # Apverčiame, kad būtų nuo seniausių iki naujausių
        features.reverse()
        
        # Konvertuojame į DataFrame
        data = []
        for feature in features:
            data.append({
                'timestamp': feature.timestamp,
                'open': feature.open,
                'high': feature.high,
                'low': feature.low,
                'close': feature.close,
                'volume': feature.volume,
                
                # Techniniai indikatoriai
                'sma_5': feature.sma_5,
                'sma_20': feature.sma_20,
                'sma_50': feature.sma_50,
                'ema_5': feature.ema_5,
                'ema_20': feature.ema_20,
                'ema_50': feature.ema_50,
                'rsi_14': feature.rsi_14,
                'macd': feature.macd,
                'macd_signal': feature.macd_signal,
                'macd_histogram': feature.macd_histogram,
                'bb_middle': feature.bb_middle,
                'bb_upper': feature.bb_upper,
                'bb_lower': feature.bb_lower,
                'bb_width': feature.bb_width,
                
                # Lag features
                'close_lag_1': feature.close_lag_1,
                'close_lag_2': feature.close_lag_2,
                'close_lag_3': feature.close_lag_3,
                'return_lag_1': feature.return_lag_1,
                'return_lag_2': feature.return_lag_2,
                'return_lag_3': feature.return_lag_3,
                
                # Target
                'target': feature.target
            })
        
        session.close()
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Klaida gaunant naujausius duomenis: {e}")
        if 'session' in locals():
            session.close()
        return pd.DataFrame()

def get_latest_indicators():
    """
    Gauna paskutinio įrašo indikatorius
    """
    try:
        session = SessionLocal()
        
        # Gauname patį naujausią įrašą
        latest = (session.query(BtcFeatures)
                 .order_by(BtcFeatures.timestamp.desc())
                 .first())
        
        session.close()
        
        if not latest:
            return None
        
        return {
            'timestamp': latest.timestamp,
            'close': latest.close,
            'rsi_14': latest.rsi_14,
            'macd': latest.macd,
            'macd_signal': latest.macd_signal,
            'macd_histogram': latest.macd_histogram,
            'bb_upper': latest.bb_upper,
            'bb_middle': latest.bb_middle,
            'bb_lower': latest.bb_lower,
            'bb_width': latest.bb_width
        }
    except Exception as e:
        logger.error(f"Klaida gaunant naujausius indikatorius: {e}")
        if 'session' in locals():
            session.close()
        return None

def predict_next_day(model_id, horizon=1):
    """
    Prognozuoja sekančios dienos kainą
    """
    try:
        # Įkeliame modelį
        model, model_info = load_model(model_id)
        if not model:
            raise ValueError("Nepavyko įkelti modelio")
        
        # Gauname naujausius duomenis
        df = get_latest_data(days=30)
        if df.empty:
            raise ValueError("Nepavyko gauti duomenų prognozavimui")
        
        # Paimame paskutinį įrašą
        latest_data = df.iloc[-1].drop(['timestamp', 'target'])
        
        # Prognozuojame
        prediction = model.predict([latest_data])[0]
        probability = model.predict_proba([latest_data])[0][1]  # Tikimybė kainai kilti
        
        # Paruošiame duomenis grafikui
        dates = df['timestamp'].dt.strftime('%Y-%m-%d').tolist()
        prices = df['close'].tolist()
        
        # Pridedame prognozuojamas datas ir kainas
        predicted_prices = prices.copy()
        future_dates = []
        
        last_date = df['timestamp'].iloc[-1]
        last_price = df['close'].iloc[-1]
        
        # Prognozuojame kainas
        next_price = last_price
        for i in range(horizon):
            next_date = last_date + timedelta(days=i+1)
            future_dates.append(next_date.strftime('%Y-%m-%d'))
            
            # Jei prognozė teigiama (kils), padidiname kainą ~1%
            # Jei neigiama (kris), sumažiname kainą ~1%
            change = 0.01 if prediction == 1 else -0.01
            next_price = next_price * (1 + change)
            predicted_prices.append(next_price)
        
        # Sujungiame datas
        all_dates = dates + future_dates
        
        # Grąžiname prognozės rezultatą
        return {
            'prediction': int(prediction),
            'probability': float(probability),
            'dates': all_dates,
            'prices': prices + [None] * horizon,  # Pridedame None, kad būtų matomas tik prognozės taškas
            'predicted_prices': [None] * len(prices) + predicted_prices[-horizon:]  # Pridedame None, kad grafikas būtų aiškesnis
        }
    except Exception as e:
        logger.error(f"Klaida prognozuojant: {e}")
        return {
            'error': str(e)
        }