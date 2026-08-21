"""
Módulo de descarga y carga de datos para Inside Airbnb y datasets complementarios.
Permite descargar de forma automatizada las últimas versiones disponibles de NYC, CDMX y Buenos Aires.
"""

import os
import re
import urllib.request
import pandas as pd
from pathlib import Path
from typing import Optional, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "selected" / "airbnb"
RAW_DIR = DATA_DIR / "raw"

CITY_SLUGS = {
    "nyc": "new-york-city",
    "cdmx": "mexico-city",
    "buenos_aires": "buenos-aires",
}


def get_latest_urls(city_key: str = "nyc") -> Dict[str, str]:
    """
    Rastrea insideairbnb.com para obtener las URLs de descarga directa más recientes para una ciudad.
    """
    slug = CITY_SLUGS.get(city_key.lower(), city_key)
    index_url = "https://insideairbnb.com/get-the-data/"
    req = urllib.request.Request(index_url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")

    # Encontrar el bloque de la ciudad más reciente
    pattern = rf"(https?://data\.insideairbnb\.com/[^\"]+/{slug}/(\d{{4}}-\d{{2}}-\d{{2}})/data/listings\.csv\.gz)"
    matches = re.findall(pattern, html)
    
    if not matches:
        raise ValueError(f"No se encontraron enlaces para la ciudad: {city_key} (slug: {slug})")
    
    latest_listing_url, date_str = matches[0]
    base_data_url = latest_listing_url.rsplit("/", 1)[0]
    
    return {
        "city": city_key,
        "date": date_str,
        "listings_detailed": f"{base_data_url}/listings.csv.gz",
        "reviews_detailed": f"{base_data_url}/reviews.csv.gz",
        "calendar_detailed": f"{base_data_url}/calendar.csv.gz",
        "neighbourhoods_geojson": f"{base_data_url.replace('/data', '/visualisations')}/neighbourhoods.geojson",
    }


def download_file(url: str, dest_path: Path, chunk_size: int = 1024 * 1024) -> Path:
    """Descarga un archivo con reporte de progreso simple."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📥 Descargando desde: {url}")
    print(f"📁 Guardando en: {dest_path}")
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                mb_down = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r  Progreso: {percent:.1f}% ({mb_down:.1f} MB / {mb_total:.1f} MB)", end="")
    print("\n✅ Descarga completada con éxito.")
    return dest_path


def load_raw_listings(city: str = "nyc", sample_size: Optional[int] = None) -> pd.DataFrame:
    """
    Carga el archivo listings.csv.gz crudo de la ciudad seleccionada.
    Si no existe localmente, lo descarga automáticamente.
    """
    city_dir = RAW_DIR / city
    dest_path = city_dir / "listings.csv.gz"
    
    if not dest_path.exists():
        urls = get_latest_urls(city)
        download_file(urls["listings_detailed"], dest_path)
        
    print(f"📖 Cargando {dest_path}...")
    df = pd.read_csv(dest_path, compression="gzip", low_memory=False, nrows=sample_size)
    print(f"📊 Dataset cargado: {df.shape[0]:,} filas x {df.shape[1]} columnas.")
    return df


if __name__ == "__main__":
    import sys
    city = sys.argv[1] if len(sys.argv) > 1 else "nyc"
    print(f"=== Descargando dataset Inside Airbnb para: {city.upper()} ===")
    urls = get_latest_urls(city)
    print(f"Fecha de corte del dataset: {urls['date']}")
    
    city_raw_dir = RAW_DIR / city
    # Descargamos el archivo principal de listings
    download_file(urls["listings_detailed"], city_raw_dir / "listings.csv.gz")
    print(f"\nListo. Archivo almacenado en: {city_raw_dir / 'listings.csv.gz'}")
