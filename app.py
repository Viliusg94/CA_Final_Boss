"""
Pagrindinis Flask aplikacijos failas.
"""
from flask import Flask, render_template
import os
import sys
import logging

# Pridedame projekto direktoriją į kelią - tai labai svarbu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Registruojame logerį
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Sukuriame Flask aplikaciją
app = Flask(__name__)

# Bazinis maršrutas tiesiogiai apibrėžtas app.py faile
@app.route('/')
def index():
    return render_template('index.html', title="BTC Prognozavimo Sistema")

# Papildomas testavimo maršrutas
@app.route('/test')
def test():
    return "Flask veikia!"

# Registruojame Blueprint maršrutus
from routes.main_routes import main
from routes.training_routes import training
from routes.prediction_routes import prediction

app.register_blueprint(main)
app.register_blueprint(training)
app.register_blueprint(prediction)

logger.info("Flask aplikacija inicializuota")

# Paleidimo kodas
if __name__ == '__main__':
    logger.info("Paleidžiama Flask aplikacija")
    app.run(debug=True, host='0.0.0.0', port=5000)