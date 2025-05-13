# Bitcoin Kainų Analizės Sistema

## 📖 Aprašymas

Ši sistema skirta Bitcoin kainų analizei ir prognozavimui. Ji leidžia:

- Gauti ir analizuoti istorinius Bitcoin kainų duomenis
- Atlikti techninius rodiklius (MA, RSI, MACD ir kt.)
- Analizuoti naujienų sentimentą
- Sukurti ir treniruoti prognozavimo modelius
- Išsaugoti ir valdyti duomenis duomenų bazėje

## 🚀 Pradžia

### Reikalavimai

- Python 3.8+
- MySQL duomenų bazė

### Instaliacijos instrukcijos

1. Sukurkite virtualią aplinką:

```
python -m venv venv
```

2. Aktyvuokite virtualią aplinką:

   - Windows:

   ```
   venv\Scripts\activate
   ```

   - Linux/Mac:

   ```
   source venv/bin/activate
   ```

3. Įdiekite reikalingus paketus:

```
pip install -r requirements.txt
```

4. Sukonfigūruokite duomenų bazės prisijungimą:

```
python -m database.test_connection
```

## 🔍 Duomenų paruošimas ir transformacijos

Sistema gali automatiškai gauti ir apdoroti Bitcoin kainų duomenis:

### Duomenų gavimas

```python
from data.btc_data import gauti_btc_kainas

# Gauti duomenis už pastaruosius 2 metus
duomenys = gauti_btc_kainas(periodas="2y", intervalas="1d")
```

### Techniniai rodikliai

```python
from data.btc_data import paruosti_duomenis

# Gauti duomenis su visais techniniais rodikliais
pilni_duomenys = paruosti_duomenis(periodas="2y", intervalas="1d")
```

Pridedami techniniai rodikliai:

- Slankieji vidurkiai (7, 30, 90 dienų SMA ir EMA)
- RSI (santykinis stiprumo indeksas)
- MACD (judančio vidurkio konvergencijos-divergencijos indikatorius)
- Bollinger juostos
- Kainų pokyčiai ir grąžos rodikliai
- Kintamumo (volatility) rodikliai

### Sentimento analizė

```python
from data.sentiment_analysis import analizuoti_naujienu_sentimenta

# Gauti Bitcoin naujienų sentimento analizę
sentimentas = analizuoti_naujienu_sentimenta(max_straipsniu=5)
```

## 🗄️ Duomenų bazės valdymas

Sistema naudoja SQLAlchemy ORM darbui su duomenų baze:

```python
from database.test_connection import engine, SessionLocal, Base
from database.test_connection import BtcPrice

# Sukurti sesiją
db = SessionLocal()

# Gauti visus Bitcoin kainų įrašus
btc_kainos = db.query(BtcPrice).all()

# Uždaryti sesiją
db.close()
```

## 📊 Pavyzdžiai

Demonstracinių pavyzdžių rasite `examples` kataloge:

- `db_example.py` - duomenų bazės naudojimo pavyzdys
- `data_preparation_example.py` - duomenų paruošimo ir transformacijų pavyzdys

## 📁 Projekto struktūra

```
.
├── app/                # Pagrindinis aplikacijos modulis
├── data/               # Duomenų gavimo ir apdorojimo moduliai
│   ├── __init__.py
│   ├── btc_data.py     # Bitcoin kainų gavimas ir apdorojimas
│   └── sentiment_analysis.py  # Naujienų sentimento analizė
├── database/           # Duomenų bazės konfigūracija ir modeliai
│   ├── __init__.py
│   ├── config.py       # DB konfigūracija
│   ├── create_env.py   # Aplinkos kintamųjų kūrimas
│   ├── init_db.py      # DB inicializacija
│   └── test_connection.py  # DB prisijungimo testavimas
├── examples/           # Pavyzdžiai
├── models/             # Duomenų modeliai/lentelės
│   ├── __init__.py
│   └── models.py
├── notebooks/          # Jupyter Notebooks analizei
├── tests/              # Testai
└── utils/              # Pagalbinės funkcijos
```

## 👨‍💻 Autoriai

- Junior Programuotojas BTC Analizei - 2025
