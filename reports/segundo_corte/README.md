# 📦 Entregables del Segundo Corte - Proyecto de Ciencia de Datos (X Semestre)
## Caso de Estudio: Modelo Predictivo y de Inteligencia de Mercado (Inside Airbnb NYC)

Bienvenido a la documentación y entregables oficiales correspondientes al **Segundo Corte** de la asignatura de **Ciencia de Datos**. Este repositorio consolida la aplicación formal de la metodología **CRISP-DM** en sus fases de **Comprensión de Datos (Data Understanding)** y **Preparación de Datos (Data Preparation)**, alineando las técnicas vistas en clase con las preguntas de negocio formuladas en el [Project Charter V0.1](file:///Users/jyarar/projects/u/x-semestre/data-science/plantilla_project_charter_v0_1.md).

---

## 🗺️ Estructura de Entregables del Segundo Corte

```
data-science/
├── data/
│   ├── backup/                                     # Copia de seguridad del Excel original de clase
│   │   └── BASE_DATOS_VIVEROS_MAYO_2026_ORIGINAL.xlsx
│   └── selected/airbnb/processed/segundo_corte/    # DATASETS LIMPIOS Y EXPORTADOS
│       ├── airbnb_nyc_limpio.csv                   # Dataset limpio en CSV (64 MB)
│       ├── airbnb_nyc_limpio.xlsx                  # Dataset limpio en Excel para inspección (25 MB)
│       └── airbnb_nyc_limpio.parquet               # Dataset limpio en Parquet para ML (15 MB)
├── notebooks/
│   ├── bitacoras_clase/                            # Talleres y bitácoras prácticas de clase
│   └── segundo_corte/                              # NOTEBOOKS EJECUTABLES OFICIALES
│       ├── 01_auditoria_calidad_airbnb.ipynb       # Fase 2: Auditoría, nulos y técnicas de clase
│       ├── 02_limpieza_transformacion_pipeline.ipynb # Fase 3: Pipeline paso a paso y exportación
│       └── 03_eda_bivariado_y_preguntas_negocio.ipynb# EDA bivariado y 5 preguntas de negocio
└── reports/
    └── segundo_corte/                              # INFORMES TÉCNICOS EN MARKDOWN (.md)
        ├── README.md                               # Este archivo
        ├── 01_reporte_auditoria_calidad.md         # Diagnóstico de calidad, nulos y tipologías
        ├── 02_estrategia_limpieza_y_transformacion.md # Reglas aplicadas y balance antes vs después
        └── 03_analisis_eda_y_hallazgos_negocio.md  # Respuestas sustentadas a preguntas de negocio
```

---

## 📑 Resumen de los Informes Técnicos

1. **[01_reporte_auditoria_calidad.md](file:///Users/jyarar/projects/u/x-semestre/data-science/reports/segundo_corte/01_reporte_auditoria_calidad.md):**
   * Perfilado de las 30,259 filas y 90 columnas crudas.
   * Diagnóstico de integridad (filas vacías, incompletas por umbral y duplicados).
   * Clasificación de nulos: 12 columnas estructuralmente vacías, 28.9% de ausencia en `price`, y ~33% en recámaras/camas.
   * Diagnóstico de tipos no tabulares (moneda con `$`, baños en texto libre y `amenities` en JSON).

2. **[02_estrategia_limpieza_y_transformacion.md](file:///Users/jyarar/projects/u/x-semestre/data-science/reports/segundo_corte/02_estrategia_limpieza_y_transformacion.md):**
   * Justificación teórica de cada regla de exclusión, depuración e imputación semántica.
   * Binarización de 26 comodidades clave y cálculo de distancias geodésicas (Haversine) a hitos turísticos (Times Square, Central Park, Brooklyn Bridge, Financial District).
   * Generación y validación de los archivos limpios en formatos `.csv`, `.xlsx` y `.parquet` para asegurar continuidad inmediata al Tercer Corte (Modelado ML).

3. **[03_analisis_eda_y_hallazgos_negocio.md](file:///Users/jyarar/projects/u/x-semestre/data-science/reports/segundo_corte/03_analisis_eda_y_hallazgos_negocio.md):**
   * Respuestas cuantitativas a las 5 preguntas analíticas planteadas en el [Project Charter V0.1](file:///Users/jyarar/projects/u/x-semestre/data-science/plantilla_project_charter_v0_1.md).
   * Cuantificación del impacto de la capacidad, comodidades premium, distancia a Manhattan y condición de *Superhost*.

---

## 🚀 Cómo Retomar para el Tercer Corte (Machine Learning)

Para iniciar el **Tercer Corte** (entrenamiento de modelos predictivos, validación cruzada y explicabilidad con SHAP), simplemente se debe cargar el dataset limpio ya preparado desde:

```python
import pandas as pd
df = pd.read_parquet("data/selected/airbnb/processed/segundo_corte/airbnb_nyc_limpio.parquet")
# o si se prefiere CSV/Excel:
# df = pd.read_csv("data/selected/airbnb/processed/segundo_corte/airbnb_nyc_limpio.csv")
```
