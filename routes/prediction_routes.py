"""
Maršrutai, susiję su prognozavimu
"""
from flask import Blueprint, render_template, request, jsonify
import logging
from datetime import datetime, timedelta
import random

# Temporary function to simulate prediction
def get_mock_models():
    """Returns mock ML models"""
    return [
        {'id': 1, 'name': 'RandomForest_20250513', 'accuracy': 0.85},
        {'id': 2, 'name': 'GradientBoosting_20250512', 'accuracy': 0.82},
        {'id': 3, 'name': 'SVM_20250510', 'accuracy': 0.79}
    ]

def predict_next_day(model_id, horizon=1):
    """Mock prediction function"""
    # Generate some dates
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
    
    # Generate mock price data
    prices = [random.uniform(50000, 70000) for _ in range(30)]
    
    # Generate future dates
    future_dates = [(datetime.now() + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1, horizon+1)]
    
    # Generate prediction (1=up, 0=down)
    prediction = random.choice([0, 1])
    
    # Calculate future prices based on prediction
    predicted_prices = []
    last_price = prices[-1]
    for _ in range(horizon):
        change = 0.01 if prediction == 1 else -0.01
        last_price = last_price * (1 + change)
        predicted_prices.append(last_price)
    
    return {
        'prediction': prediction,
        'probability': random.uniform(0.6, 0.9),
        'dates': dates + future_dates,
        'prices': prices + [None] * horizon,
        'predicted_prices': [None] * 30 + predicted_prices,
        'indicators': {
            'rsi_14': random.uniform(20, 80),
            'macd': random.uniform(-200, 200),
            'bb_width': random.uniform(0.01, 0.2)
        }
    }

logger = logging.getLogger(__name__)

prediction = Blueprint('prediction', __name__, url_prefix='/predict')

@prediction.route('', methods=['GET', 'POST'])
def predict():
    """Prognozavimo puslapis"""
    available_models = get_mock_models()
    
    prediction_result = None
    
    if request.method == 'POST':
        model_id = int(request.form.get('model_id'))
        prediction_horizon = int(request.form.get('prediction_horizon', 1))
        
        # Atliekame prognozę
        logger.info(f"Prognozuojama su modeliu ID: {model_id}, horizontas: {prediction_horizon}")
        prediction_result = predict_next_day(model_id, prediction_horizon)
    
    return render_template('predict.html', 
                          title="Bitcoin prognozė",
                          available_models=available_models,
                          prediction_result=prediction_result)

@prediction.route('/test')
def test():
    """Testavimo puslapis"""
    return "Prognozavimo blueprint veikia!"