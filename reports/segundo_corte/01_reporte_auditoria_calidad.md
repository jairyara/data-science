# 📋 Reporte 1: Auditoría de Calidad y Perfilado de Datos
## Proyecto de Ciencia de Datos (X Semestre) - Segundo Corte
### Caso de Estudio: Inside Airbnb (New York City)

---

## 1. Ficha Técnica del Dataset Evaluado

* **Fuente:** Inside Airbnb Open Data Initiative ([https://insideairbnb.com/get-the-data/](https://insideairbnb.com/get-the-data/)).
* **Ciudad / Caso de Estudio:** New York City (NYC), Estados Unidos.
* **Archivo Fuente:** `data/selected/airbnb/raw/nyc/listings.csv.gz`.
* **Volumetría Cruda:** **30,259 filas** y **90 columnas**.
* **Objetivo de Negocio:** Optimización de tarifas diarias (*Dynamic Pricing*) y cuantificación del valor marginal de comodidades y micro-localización.

---

## 2. Aplicación de las Técnicas de Diagnóstico Vistas en Clase

Siguiendo las prácticas metodológicas abordadas en los talleres del curso (auditoría en `notebooks/bitacoras_clase/`), se aplicaron los procedimientos de diagnóstico de integridad estructural:

| Prueba Diagnóstica | Método en Código | Resultado en Inside Airbnb NYC | Interpretación Metodológica |
| :--- | :--- | :---: | :--- |
| **Detección de Filas 100% Vacías** | `df.isna().all(axis=1).sum()` | **0** | No existen registros fantasma o saltos de línea vacíos generados por el scraping. |
| **Filas Incompletas por Umbral** | `(df.notna().sum(axis=1) <= 15).sum()` | **0** | Todas las propiedades tienen más de 15 atributos poblados; no hay filas fragmentadas. |
| **Duplicados Exactos** | `df.duplicated().sum()` | **0** | No hay filas íntegramente duplicadas en el archivo tabular. |
| **Duplicados por Clave Primaria (`id`)** | `df['id'].duplicated().sum()` | **0** | La unicidad de la clave primaria `id` está garantizada (1 identificador = 1 propiedad). |

---

## 3. Matriz de Completitud y Diagnóstico de Valores Ausentes (*Missingness*)

La auditoría reveló que la ausencia de datos no es homogénea y responde a tres naturalezas distintas:

### 3.1. Columnas Estructuralmente Vacías (100% Nulos)
Doce columnas del esquema original carecen completamente de datos en esta captura del dataset:
* `host_response_time`, `host_response_rate`, `host_acceptance_rate`, `host_since`, `host_verifications`, `host_total_listings_count`, `host_neighbourhood`, `host_thumbnail_url`.
* `neighborhood_overview`, `neighbourhood`, `instant_bookable`, `calendar_updated`.

> **Decisión:** Estas 12 columnas no aportan señal predictiva y deben ser descartadas para evitar ruido e hipertrofia de columnas en el pipeline de modelado.

### 3.2. Ausencia en la Variable Objetivo (`price`)
* **Registros sin precio:** **8,744 propiedades (28.90%)**.
* **Causa de negocio:** Corresponden a listados inactivos, deshabilitados por anfitriones o propiedades con bloqueo temporal en el calendario durante la fecha del raspado.
* **Decisión metodológica:** En aprendizaje supervisado para regresión, **no es metodológicamente válido imputar la variable objetivo**. Estos 8,744 registros deben excluirse del conjunto de entrenamiento y prueba.

### 3.3. Ausencia en Infraestructura Habitacional (Imputación Justificada)
* `bedrooms`: 10,973 nulos (**36.26%**).
* `bathrooms`: 10,112 nulos (**33.42%**).
* `beds`: 9,419 nulos (**31.13%**).
* **Causa de negocio:** Muchos alojamientos tipo estudio (*studio apartments*) o habitaciones tipo loft no declaran recámaras separadas (`bedrooms = NaN`), aunque sí reportan su capacidad total de huéspedes (`accommodates`).
* **Decisión metodológica:** Realizar **imputación semántica basada en reglas de dominio**: un alojamiento con `accommodates = 2` y `bedrooms = NaN` tiene al menos 1 espacio para dormir; `bedrooms` se imputa con $\lceil \text{accommodates} / 2 \rceil$.

### 3.4. Ausencia en Métricas de Reputación
* `review_scores_rating`, `reviews_per_month`: 7,931 nulos (**26.21%**).
* **Causa de negocio:** *Missing Not at Random (MNAR)*. Corresponden a propiedades nuevas o inactivas que nunca han recibido reservas ni reseñas (`number_of_reviews = 0`).
* **Decisión metodológica:** Crear un flag indicador `has_reviews` (0 o 1), imputar `reviews_per_month` con 0.0, e imputar `review_scores_rating` con la mediana general de propiedades con historial para no penalizar artificialmente a listados nuevos.

---

## 4. Diagnóstico de Tipos de Datos Corruptos y No Tabulares

1. **Campos Monetarios como Cadenas de Texto (`price`):**
   * Vienen formateados con signos de dólar, comas de miles y decimales (ej. `"$1,250.00"`).
   * Requieren expresión regular `re.sub(r"[^\d.]", "", val)` para conversión estricta a tipo `float64`.
2. **Número de Baños en Texto Libre (`bathrooms_text`):**
   * Contiene descripciones mixtas: `"1 bath"`, `"1.5 baths"`, `"Half-bath"`, `"Shared half-bath"`, `"Private half-bath"`.
   * Requiere parser semántico: `"Half-bath"` $\rightarrow 0.5$; `"1.5 baths"` $\rightarrow 1.5$.
3. **Comodidades Anidadas en Formato JSON (`amenities`):**
   * Cadenas con sintaxis `["Wifi", "Air conditioning", "Kitchen"]`.
   * No son explotables en formato plano; requieren deserialización con `json.loads()` y extracción a columnas booleanas (0/1).
4. **Booleanos en Formato Texto:**
   * Variables como `host_is_superhost`, `host_identity_verified`, `has_availability` almacenan cadenas `'t'` o `'f'`.
   * Requieren mapeo directo a valores enteros binarios ($1 / 0$).

---

## 5. Auditoría de Valores Atípicos (*Outliers*) y Regulación de NYC

### 5.1. Precios Extremos y Errores de Entrada
* Existen propiedades con precio de **\$0.00 USD** (errores operacionales o promociones ficticias) y valores superiores a **\$10,000 USD/noche** que representan listados con fines de bloqueo de calendario.
* **Filtro propuesto:** Retener alojamientos con tarifas entre **\$10.00 USD** y **\$2,000.00 USD/noche**, preservando el 99.2% de la distribución real y eliminando el ruido que desestabiliza modelos de Machine Learning.

### 5.2. Estancia Mínima (`minimum_nights`) y Ley Local 18 (*Local Law 18*)
* La regulación municipal de NYC implementada en 2023 exige registros estrictos para alquileres de menos de 30 días.
* **Distribución observada en el dataset:**
  * Estancias cortas ($< 30$ días): **5,308 listados (17.5%)**.
  * Estancias de media/larga duración ($\ge 30$ días): **24,951 listados (82.5%)**.
* Esta dinámica demuestra el reacomodo del mercado turístico neoyorquino hacia estancias mensuales o contratos de media temporada, un factor determinante para contextualizar las recomendaciones a los anfitriones.

---

## 6. Síntesis Diagnóstica para el Segundo Corte

| Dimensión Auditada | Estado Inicial | Acción Metodológica Ejecutada en Limpieza |
| :--- | :--- | :--- |
| **Completitud de Registros** | 30,259 filas brutas | Purgar registros sin variable objetivo (`price` nulo). |
| **Calidad de Target** | Moneda en texto con outliers | Parsear a `price_usd`, aplicar logaritmo `log_price` y acotar en [\$10, \$2000]. |
| **Variables Faltantes** | 12 columnas vacías (100% NaN) | Descartadas de la matriz de características. |
| **Imputación Habitacional** | ~33% nulos en dormitorios y camas | Imputación semántica ligada a la capacidad `accommodates`. |
| **Comodidades** | Listas JSON no tabulares | Extracción de 26 variables indicadoras binarias. |
