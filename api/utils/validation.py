import os
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns

PLOTS_DIR_PATH = "../images/plots"

# --- Functions ---------------------------------------------------------------------------------

# ========== METRICS ==========

def calculate_metrics(y_true, y_predicted):
    '''
    returns a string containing R2 and MAE for both Train and Test.
    '''
    # R² & MAE
    r2 = r2_score(y_true, y_predicted)
    mae = mean_absolute_error(y_true, y_predicted)
    rmse = np.sqrt(mean_squared_error(y_true, y_predicted))

    metrics = {
        'R²': f'{round((r2 * 100), 2)} %',
        'MAE': f'{mae:,.2f} €',
        'RMSE': f'{rmse:,.2f} €'
    }

    return metrics


def plot_predict_vs_actual(y_true, y_pred):
    """
    Generates and saves a scatter plot comparing actual prices vs. model predictions.
    """
    os.makedirs(PLOTS_DIR_PATH, exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    
    # Scatter plot with alpha transparency to prevent overplotting issues
    sns.scatterplot(x=y_true, y=y_pred, alpha=0.4, color='#1f77b4', edgecolor='none')
    
    # Perfect alignment reference line (y = x)
    max_val = max(max(y_true), max(y_pred))
    min_val = min(min(y_true), min(y_pred))
    plt.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--', linewidth=2, label='Perfect Prediction')
    
    plt.title('Actual vs. Predicted Prices (XGBoost)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Actual Price (€)', fontsize=12)
    plt.ylabel('Predicted Price (€)', fontsize=12)
    
    # Format axes ticks with thousand separators
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    # Save chart to the assets structure
    plot_path = os.path.join(PLOTS_DIR_PATH, "predict_vs_actual.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"📊 'Predict vs Actual' chart successfully saved at: {plot_path}")