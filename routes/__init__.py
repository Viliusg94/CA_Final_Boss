"""
Maršrutų registravimas
"""
from flask import Flask
from .main_routes import main
from .training_routes import training
from .prediction_routes import prediction

def register_routes(app: Flask):
    """Registruoja visus maršrutus"""
    app.register_blueprint(main)
    app.register_blueprint(training)
    app.register_blueprint(prediction)