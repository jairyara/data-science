"""
Módulo de Limpieza y Preprocesamiento de Datos para Inside Airbnb.
Transforma variables crudas, sucias y anidadas en formatos tabulares estándar.
"""

import re
import json
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


def parse_currency(val) -> float:
    """Convierte cadenas con símbolos de moneda y comas a float."""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    # Remover $ , y espacios
    clean_val = re.sub(r"[^\d.]", "", str(val))
    try:
        return float(clean_val)
    except ValueError:
        return np.nan


def parse_bathrooms(val) -> float:
    """Extrae el número de baños a partir de texto libre."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).lower().strip()
    if "half" in val_str:
        return 0.5
    match = re.search(r"(\d+(\.\d+)?)", val_str)
    return float(match.group(1)) if match else np.nan


def parse_amenities_json(val) -> List[str]:
    """Parsea el campo textual de comodidades a una lista de Python."""
    if pd.isna(val):
        return []
    try:
        items = json.loads(val)
        return [str(i).strip().lower() for i in items if str(i).strip()]
    except Exception:
        # Fallback para cadenas no-JSON
        return [i.strip(" \"'[]").lower() for i in str(val).split(",") if i.strip(" \"'[]")]


# Comodidades clave identificadas con impacto en valor inmobiliario y turístico
KEY_AMENITIES = [
    "wifi",
    "air conditioning",
    "kitchen",
    "dedicated workspace",
    "washer",
    "dryer",
    "elevator",
    "pool",
    "hot tub",
    "free parking",
    "paid parking",
    "iron",
    "hair dryer",
    "tv",
    "refrigerator",
    "microwave",
    "coffee maker",
    "dishes and silverware",
    "self check-in",
    "smoke alarm",
    "carbon monoxide alarm",
    "fire extinguisher",
    "first aid kit",
    "bathtub",
    "patio or balcony",
    "gym",
]


def extract_amenity_features(df: pd.DataFrame, key_amenities: Optional[List[str]] = None) -> pd.DataFrame:
    """Genera columnas booleanas (0/1) para las comodidades más influyentes."""
    if key_amenities is None:
        key_amenities = KEY_AMENITIES

    amenities_series = df["amenities"].apply(parse_amenities_json)
    
    amenity_df = pd.DataFrame(index=df.index)
    for amenity in key_amenities:
        col_name = f"has_{amenity.replace(' ', '_').replace('/', '_')}"
        amenity_df[col_name] = amenities_series.apply(
            lambda items: 1 if any(amenity in item for item in items) else 0
        ).astype(int)
    
    # Característica adicional: conteo total de comodidades ofrecidas
    amenity_df["total_amenities_count"] = amenities_series.apply(len)
    return amenity_df


def clean_airbnb_dataset(
    df: pd.DataFrame,
    min_price: float = 10.0,
    max_price: float = 2000.0,
    max_min_nights: int = 365
) -> pd.DataFrame:
    """
    Ejecuta el pipeline completo de limpieza sobre el dataset crudo:
    1. Parseo de columnas de precio y baños.
    2. Imputación semántica y conversión de tipos.
    3. Extracción de comodidades estructuradas.
    4. Filtrado justificado de valores anómalos/outliers.
    """
    df_clean = df.copy()

    # 1. Limpieza de target y variables numéricas corruptas
    df_clean["price_usd"] = df_clean["price"].apply(parse_currency)
    df_clean["bathrooms_num"] = df_clean["bathrooms_text"].apply(parse_bathrooms)

    # 2. Filtrado de registros sin precio válido o con outliers extremos
    valid_mask = (
        df_clean["price_usd"].notna()
        & (df_clean["price_usd"] >= min_price)
        & (df_clean["price_usd"] <= max_price)
    )
    df_clean = df_clean[valid_mask].copy()

    # 3. Filtrado de reglas absurdas de estancia mínima (errores de entrada)
    if "minimum_nights" in df_clean.columns:
        df_clean = df_clean[df_clean["minimum_nights"] <= max_min_nights].copy()

    # 4. Imputación inteligente de recámaras y camas basadas en capacidad
    df_clean["accommodates"] = df_clean["accommodates"].fillna(1).clip(lower=1)
    df_clean["bedrooms_num"] = df_clean["bedrooms"].fillna(
        np.ceil(df_clean["accommodates"] / 2)
    )
    df_clean["beds_num"] = df_clean["beds"].fillna(df_clean["bedrooms_num"])
    df_clean["bathrooms_num"] = df_clean["bathrooms_num"].fillna(1.0)

    # 5. Extracción de variables de comodidades
    amenities_features = extract_amenity_features(df_clean)
    df_clean = pd.concat([df_clean, amenities_features], axis=1)

    # 6. Target logarítmico para modelos de regresión lineal y gradiente
    df_clean["log_price"] = np.log1p(df_clean["price_usd"])

    return df_clean
