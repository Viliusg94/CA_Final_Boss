"""
Grafikų generavimo paslaugos
"""
import pandas as pd
import numpy as np
import logging
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

def create_price_chart(dates, prices, predicted_dates=None, predicted_prices=None):
    """
    Sukuria kainos grafiką
    
    Grąžina:
        base64 koduotą paveikslėlį
    """
    try:
        plt.figure(figsize=(10, 6))
        
        # Braižome faktines kainas
        plt.plot(dates, prices, label='Faktinė kaina', color='blue', marker='o')
        
        # Braižome prognozuojamas kainas, jei jos pateiktos
        if predicted_dates and predicted_prices:
            plt.plot(predicted_dates, predicted_prices, label='Prognozė', color='red', 
                    linestyle='--', marker='s')
        
        plt.title('Bitcoin kainos')
        plt.xlabel('Data')
        plt.ylabel('Kaina (USD)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Pasukame x ašies etiketes, kad būtų lengviau skaityti
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Išsaugome paveikslėlį į atminties buferį
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Koduojame į base64
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        logger.error(f"Klaida kuriant kainos grafiką: {e}")
        return None

def create_feature_importance_chart(feature_names, feature_importance):
    """
    Sukuria požymių svarbos grafiką
    
    Grąžina:
        base64 koduotą paveikslėlį
    """
    try:
        plt.figure(figsize=(10, 6))
        
        # Sukuriame horizontalų juostinį grafiką
        y_pos = np.arange(len(feature_names))
        plt.barh(y_pos, feature_importance, align='center')
        plt.yticks(y_pos, feature_names)
        
        plt.title('Požymių svarba')
        plt.xlabel('Svarba')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Išsaugome paveikslėlį į atminties buferį
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Koduojame į base64
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        logger.error(f"Klaida kuriant požymių svarbos grafiką: {e}")
        return None