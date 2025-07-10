# app/ml/ml_services.py
import pandas as pd
import numpy as np
import joblib
from app.use_cases.data_processing_use_case import extract_features


def process_model(input_data, db=None):
    """
    Process input data and predict real estate price using a pre-trained model.

    Args:
        input_data (dict): Dictionary containing property features.
        db (optional): Database connection (not used currently).

    Returns:
        dict or None: Dictionary with predicted price and possible warning, or None on failure.
    """
    try:
        model = joblib.load('app/ml/price_model.pkl')
        target_encoder = joblib.load('app/ml/target_encoder.pkl')
        scaler = joblib.load('app/ml/scaler.pkl')
        feature_names = joblib.load('app/ml/feature_names.pkl')

        categorical = ['district', 'type', 'cond', 'walls']
        numeric = ['rooms', 'floor', 'floors', 'area', 'property_level', 'property_strength', 'property_area_factor',
                   'high_quality_property', 'is_luxury']

        property_weights = {
            1: 10.0,
            2: 5.0,
            3: 2.0,
            4: 0.5,
            5: 0.1
        }

        required_fields = categorical + ['rooms', 'floor', 'floors', 'area']
        missing_fields = [field for field in required_fields if field not in input_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        df = pd.DataFrame([input_data])

        warning = None

        if 'desc' in df.columns and not pd.isna(df['desc']).iloc[0]:
            features = df['desc'].apply(extract_features)
            df['property_level'] = features.apply(lambda x: x['property_level'])
            if 'warning' in features.iloc[0]:
                df['warning'] = features.apply(lambda x: x.get('warning', None))
            df = df.drop(columns=['desc'])
        else:
            df['property_level'] = 5
            df['warning'] = 'desc None (5)'


        df = df.drop(columns=['desc'], errors='ignore')

        df['property_strength'] = df['property_level'].map(property_weights)
        df['high_quality_property'] = df['property_level'].apply(lambda x: 1 if x <= 2 else 0)
        df['property_area_factor'] = df['property_strength'] * df['area']
        df['is_luxury'] = df['property_level'].apply(lambda x: 1 if x == 1 else 0)

        for col in feature_names:
            if col not in df.columns:
                df[col] = 0


        df = df[feature_names]

        df_enc = target_encoder.transform(df[categorical + numeric])
        df_enc[numeric] = scaler.transform(df_enc[numeric])
        df_enc = df_enc.reindex(columns=feature_names, fill_value=0)

        y_pred_log = model.predict(df_enc)[0]



        predicted_price = np.expm1(y_pred_log)

        return {'predicted_price': float(predicted_price), 'warning': warning}

    except Exception as e:

        return None

