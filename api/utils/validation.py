import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


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