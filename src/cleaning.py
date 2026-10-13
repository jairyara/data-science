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


def audit_dataset(df: pd.DataFrame, incomplete_threshold: int = 15) -> dict:
    """
    Ejecuta una auditoría integral de calidad de datos replicando y extendiendo
    las técnicas diagnósticas de clase:
    - Dimensiones y tipos
    - Filas 100% vacías
    - Filas incompletas por umbral
    - Duplicados totales y por clave primaria
    - Resumen y porcentaje de valores nulos
    """
    total_rows, total_cols = df.shape
    empty_rows = int(df.isna().all(axis=1).sum())
    incomplete_rows = int((df.notna().sum(axis=1) <= incomplete_threshold).sum())
    total_duplicates = int(df.duplicated().sum())
    id_duplicates = int(df["id"].duplicated().sum()) if "id" in df.columns else 0

    missing_series = df.isna().sum()
    missing_pct = (df.isna().mean() * 100).round(2)
    missing_summary = (
        pd.DataFrame({
            "columna": df.columns,
            "tipo": df.dtypes.astype(str),
            "nulos_conteo": missing_series.values,
            "nulos_porcentaje": missing_pct.values,
        })
        .sort_values(by="nulos_porcentaje", ascending=False)
        .reset_index(drop=True)
    )

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "empty_rows": empty_rows,
        "incomplete_rows": incomplete_rows,
        "total_duplicates": total_duplicates,
        "id_duplicates": id_duplicates,
        "missing_summary": missing_summary,
    }


def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas que estén completamente vacías (todas las columnas NaN)."""
    return df.dropna(how="all").copy()


def filter_incomplete_rows(df: pd.DataFrame, min_valid_cols: int = 15) -> pd.DataFrame:
    """Filtra y remueve filas con un número insuficiente de columnas con datos válidos."""
    return df[df.notna().sum(axis=1) > min_valid_cols].copy()


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """Detecta y elimina registros duplicados con reporte en consola."""
    prev_len = len(df)
    df_dedup = df.drop_duplicates(subset=subset).copy()
    diff = prev_len - len(df_dedup)
    if diff > 0:
        print(f"🗑️ Se eliminaron {diff:,} registros duplicados (subset={subset}).")
    else:
        print("✅ No se detectaron duplicados para el criterio especificado.")
    return df_dedup


def normalize_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estandariza variables categóricas y de texto:
    - Remueve espacios en blanco redundantes
    - Unifica mayúsculas/minúsculas
    - Mapea flags 't' y 'f' a booleanos estándar
    """
    df_norm = df.copy()

    # Columnas booleanas en formato de texto 't' / 'f'
    bool_text_cols = [
        "host_is_superhost",
        "host_has_profile_pic",
        "host_identity_verified",
        "has_availability",
        "instant_bookable",
    ]
    for col in bool_text_cols:
        if col in df_norm.columns:
            df_norm[col] = (
                df_norm[col]
                .astype(str)
                .str.strip()
                .str.lower()
                .map({"t": 1, "true": 1, "1": 1, "f": 0, "false": 0, "0": 0})
                .fillna(0)
                .astype(int)
            )

    # Estandarización de textos clave
    for col in ["room_type", "neighbourhood_group_cleansed"]:
        if col in df_norm.columns:
            df_norm[col] = df_norm[col].astype(str).str.strip().str.title()

    return df_norm

