"""
Módulo de Ingeniería de Características (Feature Engineering) para Inside Airbnb.
Genera variables geoespaciales, ratios de capacidad, métricas de anfitrión y encodings.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple

# Puntos de interés geográfico de referencia en NYC (Latitud, Longitud)
NYC_LANDMARKS = {
    "times_square": (40.7580, -73.9855),
    "financial_district": (40.7075, -74.0090),
    "central_park": (40.785091, -73.968285),
    "brooklyn_bridge": (40.7061, -73.9969),
}


def haversine_distance(lat1: np.ndarray, lon1: np.ndarray, lat2: float, lon2: float) -> np.ndarray:
    """
    Calcula la distancia geodésica en kilómetros entre arrays de coordenadas (Haversine).
    """
    R = 6371.0  # Radio de la Tierra en km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega características derivadas para enriquecer el poder predictivo del modelo:
    1. Distancias a centros neurálgicos y turísticos (km).
    2. Ratios de capacidad e infraestructura.
    3. Ratios de disponibilidad temporal.
    4. Métricas de reputación y reseñas.
    """
    df_feat = df.copy()

    # 1. Distancias Geográficas
    if "latitude" in df_feat.columns and "longitude" in df_feat.columns:
        lats = df_feat["latitude"].values
        lons = df_feat["longitude"].values
        for landmark, (l_lat, l_lon) in NYC_LANDMARKS.items():
            df_feat[f"dist_{landmark}_km"] = haversine_distance(lats, lons, l_lat, l_lon)
        # Distancia mínima a cualquier landmark principal
        dist_cols = [f"dist_{landmark}_km" for landmark in NYC_LANDMARKS]
        df_feat["min_dist_to_landmark_km"] = df_feat[dist_cols].min(axis=1)

    # 2. Ratios de Capacidad
    bedrooms = df_feat["bedrooms_num"].clip(lower=1)
    df_feat["accommodates_per_bedroom"] = df_feat["accommodates"] / bedrooms
    df_feat["beds_per_bedroom"] = df_feat["beds_num"] / bedrooms
    df_feat["bathrooms_per_accommodates"] = df_feat["bathrooms_num"] / df_feat["accommodates"]

    # 3. Ratios de Disponibilidad
    if "availability_30" in df_feat.columns:
        df_feat["availability_ratio_30"] = df_feat["availability_30"].clip(0, 30) / 30.0
    if "availability_365" in df_feat.columns:
        df_feat["availability_ratio_365"] = df_feat["availability_365"].clip(0, 365) / 365.0

    # 4. Métricas de Reseñas y Popularidad
    if "number_of_reviews" in df_feat.columns and "reviews_per_month" in df_feat.columns:
        df_feat["reviews_per_month_clean"] = df_feat["reviews_per_month"].fillna(0.0)
        df_feat["has_reviews"] = (df_feat["number_of_reviews"] > 0).astype(int)
        df_feat["review_scores_rating_clean"] = df_feat["review_scores_rating"].fillna(
            df_feat["review_scores_rating"].median()
        )

    # 5. Agrupamiento de tipos de propiedad poco frecuentes (Top 8 + 'Other')
    if "property_type" in df_feat.columns:
        top_properties = df_feat["property_type"].value_counts().head(8).index
        df_feat["property_type_grouped"] = df_feat["property_type"].apply(
            lambda x: x if x in top_properties else "Other"
        )

    return df_feat
