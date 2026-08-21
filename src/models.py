"""
Módulo de Modelado Predictivo, Evaluación e Interpretabilidad (SHAP) para Inside Airbnb.
Entrena modelos de regresión para Dynamic Pricing y evalúa impacto de negocio.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, median_absolute_error, r2_score
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
import lightgbm as lgb
import xgboost as xgb
import shap


def get_feature_lists() -> Tuple[List[str], List[str]]:
    """Define las listas de columnas numéricas y categóricas para el pipeline."""
    numeric_features = [
        "accommodates",
        "bedrooms_num",
        "beds_num",
        "bathrooms_num",
        "minimum_nights",
        "availability_365",
        "number_of_reviews",
        "reviews_per_month_clean",
        "review_scores_rating_clean",
        "dist_times_square_km",
        "dist_financial_district_km",
        "dist_central_park_km",
        "dist_brooklyn_bridge_km",
        "min_dist_to_landmark_km",
        "accommodates_per_bedroom",
        "beds_per_bedroom",
        "bathrooms_per_accommodates",
        "availability_ratio_30",
        "availability_ratio_365",
        "total_amenities_count",
    ]
    
    # Comodidades booleanas
    amenity_cols = [
        "has_wifi", "has_air_conditioning", "has_kitchen", "has_dedicated_workspace",
        "has_washer", "has_dryer", "has_elevator", "has_pool", "has_hot_tub",
        "has_free_parking", "has_paid_parking", "has_iron", "has_hair_dryer", "has_tv",
        "has_refrigerator", "has_microwave", "has_coffee_maker", "has_dishes_and_silverware",
        "has_self_check-in", "has_smoke_alarm", "has_carbon_monoxide_alarm",
        "has_fire_extinguisher", "has_first_aid_kit", "has_bathtub", "has_patio_or_balcony", "has_gym"
    ]
    numeric_features.extend(amenity_cols)

    categorical_features = [
        "neighbourhood_group_cleansed",
        "room_type",
        "property_type_grouped",
    ]

    return numeric_features, categorical_features


def build_preprocessor(numeric_cols: List[str], categorical_cols: List[str]) -> ColumnTransformer:
    """Crea el ColumnTransformer para preprocesar numéricas y categóricas."""
    numeric_transformer = Pipeline(steps=[
        ("scaler", RobustScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )
    return preprocessor


def evaluate_regression(y_true_usd: np.ndarray, y_pred_log: np.ndarray) -> Dict[str, float]:
    """
    Evalúa predicciones calculando métricas tanto en la escala transformada como en dólares reales ($USD).
    """
    # Revertir predicción logarítmica: exp(pred) - 1
    y_pred_usd = np.expm1(y_pred_log)
    y_pred_usd = np.clip(y_pred_usd, a_min=5.0, a_max=5000.0)

    rmse = np.sqrt(mean_squared_error(y_true_usd, y_pred_usd))
    mae = mean_absolute_error(y_true_usd, y_pred_usd)
    medae = median_absolute_error(y_true_usd, y_pred_usd)
    r2 = r2_score(y_true_usd, y_pred_usd)
    
    # Métricas en escala logarítmica (para comparar bondad de ajuste pura)
    y_true_log = np.log1p(y_true_usd)
    rmse_log = np.sqrt(mean_squared_error(y_true_log, y_pred_log))
    r2_log = r2_score(y_true_log, y_pred_log)

    return {
        "RMSE ($USD)": round(rmse, 2),
        "MAE ($USD)": round(mae, 2),
        "MedAE ($USD)": round(medae, 2),
        "R2 ($USD)": round(r2, 4),
        "RMSE (log scale)": round(rmse_log, 4),
        "R2 (log scale)": round(r2_log, 4),
    }


def train_benchmark_models(
    X_train_df: pd.DataFrame,
    y_train_log: np.ndarray,
    y_train_usd: np.ndarray,
    X_test_df: pd.DataFrame,
    y_test_log: np.ndarray,
    y_test_usd: np.ndarray,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Entrena y compara una suite de modelos (Baseline, Ridge, Random Forest, LightGBM, XGBoost).
    """
    num_cols, cat_cols = get_feature_lists()
    
    # Filtrar solo columnas presentes
    num_cols = [c for c in num_cols if c in X_train_df.columns]
    cat_cols = [c for c in cat_cols if c in X_train_df.columns]

    preprocessor = build_preprocessor(num_cols, cat_cols)
    
    X_train_trans = preprocessor.fit_transform(X_train_df)
    X_test_trans = preprocessor.transform(X_test_df)

    models = {
        "Baseline (Median)": DummyRegressor(strategy="median"),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1),
        "LightGBM": lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, max_depth=8, random_state=42, verbose=-1),
        "XGBoost": xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42),
    }

    results = []
    trained_models = {}

    for name, model in models.items():
        print(f"⚡ Entrenando {name}...")
        model.fit(X_train_trans, y_train_log)
        preds_log = model.predict(X_test_trans)
        
        metrics = evaluate_regression(y_test_usd, preds_log)
        metrics["Modelo"] = name
        results.append(metrics)
        trained_models[name] = {
            "model": model,
            "preprocessor": preprocessor,
            "predictions_log": preds_log,
        }

    results_df = pd.DataFrame(results).set_index("Modelo")
    return results_df, trained_models
