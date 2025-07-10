# app/ml/train_model.py
import pandas as pd
import sqlite3
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import category_encoders as ce
from ..utils.utils import Utils
import json




def calculate_metrics(y_true, y_pred, X_test, baseline_mae=None):
    """
    Calculate regression performance metrics.

    Args:
        y_true (array-like): True target values.
        y_pred (array-like): Predicted target values.
        X_test (DataFrame): Test feature data.
        baseline_mae (float, optional): Baseline MAE for MASE calculation.

    Returns:
        dict: Dictionary of various regression metrics.
    """
    metrics = {}

    metrics['MSE'] = mean_squared_error(y_true, y_pred)
    metrics['RMSE'] = np.sqrt(metrics['MSE'])

    y_true_nonzero = y_true[y_true != 0]
    y_pred_nonzero = y_pred[y_true != 0]
    if len(y_true_nonzero) > 0:
        mspe = np.mean(((y_true_nonzero - y_pred_nonzero) / y_true_nonzero) ** 2) * 100
        metrics['MSPE'] = mspe
    else:
        metrics['MSPE'] = np.nan

    metrics['MAE'] = mean_absolute_error(y_true, y_pred)

    if len(y_true_nonzero) > 0:
        mape = np.mean(np.abs((y_true_nonzero - y_pred_nonzero) / y_true_nonzero)) * 100
        metrics['MAPE'] = mape
    else:
        metrics['MAPE'] = np.nan

    smape = np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred) + 1e-10)) * 100
    metrics['SMAPE'] = smape

    if baseline_mae is None:
        naive_pred = np.full_like(y_true, np.mean(y_true))
        baseline_mae = mean_absolute_error(y_true, naive_pred)
    metrics['MASE'] = metrics['MAE'] / (baseline_mae + 1e-10)

    if len(y_true_nonzero) > 0:
        mre = np.mean(np.abs((y_true_nonzero - y_pred_nonzero) / y_true_nonzero))
        metrics['MRE'] = mre
    else:
        metrics['MRE'] = np.nan

    rmsle = np.sqrt(np.mean((np.log1p(y_true) - np.log1p(y_pred)) ** 2))
    metrics['RMSLE'] = rmsle

    metrics['R2'] = r2_score(y_true, y_pred)

    n = len(y_true)
    k = X_test.shape[1]
    if n > k + 1:
        metrics['Adjusted_R2'] = 1 - (1 - metrics['R2']) * (n - 1) / (n - k - 1)
    else:
        metrics['Adjusted_R2'] = np.nan

    return metrics

utils = Utils()

df = utils.filter_data()

property_weights = {
    1: 10.0,
    2: 5.0,
    3: 2.0,
    4: 0.5,
    5: 0.1
}

df['property_strength'] = df['property_level'].map(property_weights)

df['high_quality_property'] = df['property_level'].apply(lambda x: 1 if x <= 2 else 0)

df['property_area_factor'] = df['property_strength'] * df['area']

df['is_luxury'] = df['property_level'].apply(lambda x: 1 if x == 1 else 0)

X = df.drop(columns=['price'])

y = df['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

categorical = ['district', 'type', 'cond', 'walls']
numeric = ['rooms', 'floor', 'floors', 'area', 'property_level', 'property_strength', 'property_area_factor',
           'high_quality_property', 'is_luxury']

target_encoder = ce.TargetEncoder(cols=categorical)
X_train_enc = target_encoder.fit_transform(X_train, y_train)
X_test_enc = target_encoder.transform(X_test)

scaler = StandardScaler()
X_train_enc[numeric] = scaler.fit_transform(X_train_enc[numeric])
X_test_enc[numeric] = scaler.transform(X_test_enc[numeric])

y_train_log = np.log1p(y_train)

model = HistGradientBoostingRegressor(random_state=42)
model.fit(X_train_enc, y_train_log)

from sklearn.inspection import permutation_importance

result = permutation_importance(model, X_test_enc, y_test, n_repeats=10, random_state=42)

# importances = pd.DataFrame({
#     'feature': X_test_enc.columns,
#     'importance': result.importances_mean
# }).sort_values('importance', ascending=False)
# print(importances)

y_pred_log = model.predict(X_test_enc)
y_pred = np.expm1(y_pred_log)

metrics = calculate_metrics(y_test, y_pred, X_test_enc)

for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")

with open("metrics_results.json", "w") as f:
    json.dump({metric: round(value, 4) for metric, value in metrics.items()}, f, indent=4)

joblib.dump(model, '../price_model.pkl')
joblib.dump(target_encoder, '../target_encoder.pkl')
joblib.dump(scaler, '../scaler.pkl')
feature_names = list(X_train_enc.columns)
joblib.dump(feature_names, '../feature_names.pkl')

