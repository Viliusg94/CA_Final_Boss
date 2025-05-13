from flask import Blueprint, render_template
from database.config import SessionLocal
from database.models import MLModel

main = Blueprint('main', __name__, url_prefix='')  # Pagrindinis URL be prefikso

@main.route('/home')
def index():
    """Pradinis puslapis"""
    try:
        # Gauname paskutinius 5 modelius
        session = SessionLocal()
        models = session.query(MLModel).order_by(MLModel.created_at.desc()).limit(5).all()
        session.close()
        
        return render_template('index.html', 
                              title="BTC Prognozavimo Sistema",
                              models=models)
    except Exception as e:
        # Jei klaida, rodome pagrindinį puslapį be modelių
        return render_template('index.html', 
                              title="BTC Prognozavimo Sistema",
                              models=[])