"""
Maršrutai, susiję su modelio treniravimu
"""
from flask import Blueprint, render_template, request, jsonify
import sys
import os
import logging

# Sukuriame paprastą treniravimo simuliaciją
def train_model_with_params(model_type, test_size, params):
    """Laikina funkcija modeliui treniruoti"""
    return {
        'model_id': 1,
        'accuracy': 0.85,
        'precision': 0.82,
        'recall': 0.79,
        'f1_score': 0.80,
        'feature_importance': [0.2, 0.15, 0.1, 0.08, 0.07],
        'feature_names': ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
    }

logger = logging.getLogger(__name__)

training = Blueprint('training', __name__, url_prefix='/train')

@training.route('', methods=['GET', 'POST'])
def train():
    """Modelio treniravimo puslapis"""
    training_result = None
    
    if request.method == 'POST':
        # Gauname parametrus iš formos
        model_type = request.form.get('model_type', 'random_forest')
        test_size = float(request.form.get('test_size', 0.2))
        
        # Parametrai pagal modelio tipą
        params = {}
        
        if model_type == 'random_forest':
            params['n_estimators'] = int(request.form.get('n_estimators', 100))
            params['max_depth'] = int(request.form.get('max_depth', 10))
        elif model_type == 'gradient_boosting':
            params['learning_rate'] = float(request.form.get('learning_rate', 0.1))
        elif model_type == 'svm':
            params['C'] = float(request.form.get('C', 1.0))
        
        # Treniruojame modelį
        logger.info(f"Pradedamas modelio treniravimas su parametrais: {params}")
        training_result = train_model_with_params(model_type, test_size, params)
        
    return render_template('train.html', 
                          title="Modelio treniravimas",
                          training_result=training_result)

@training.route('/test')
def test():
    """Testavimo puslapis"""
    return "Treniravimo blueprint veikia!"

@training.route('/api/train', methods=['POST'])
def api_train():
    """API modelio treniravimui"""
    try:
        data = request.get_json()
        model_type = data.get('model_type', 'random_forest')
        test_size = float(data.get('test_size', 0.2))
        params = data.get('params', {})
        
        training_result = train_model_with_params(model_type, test_size, params)
        
        return jsonify({
            'success': True,
            'model_id': training_result.get('model_id'),
            'accuracy': training_result.get('accuracy'),
            'precision': training_result.get('precision'),
            'recall': training_result.get('recall'),
            'f1_score': training_result.get('f1_score')
        })
    except Exception as e:
        logger.error(f"Klaida API treniravime: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500