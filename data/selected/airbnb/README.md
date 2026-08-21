# Inside Airbnb Dataset (Dataset Seleccionado)

Este directorio está destinado a almacenar los datos crudos y procesados de **Inside Airbnb**.

## Fuentes de Descarga Abierta
Inside Airbnb ofrece datasets abiertos y actualizados por ciudad en:
- **URL oficial**: [http://insideairbnb.com/get-the-data/](http://insideairbnb.com/get-the-data/)

### Archivos recomendados para descargar (ejemplo: New York City, Madrid, etc.):
1. `listings.csv.gz` - Datos detallados de alojamientos (+75 columnas).
2. `reviews.csv.gz` - Reseñas completas de los huéspedes.
3. `calendar.csv.gz` - Datos diarios de disponibilidad y precios.
4. `neighbourhoods.geojson` - Polígonos de barrios para visualización geoespacial.

## Subcarpetas sugeridas
- `raw/`: Archivos `.csv.gz` o `.csv` originales sin modificar.
- `processed/`: Tablas limpias y transformadas tras la Fase 3 del pipeline.
