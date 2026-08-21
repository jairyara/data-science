# Proyecto de Ciencia de Datos - X Semestre

Repositorio para el desarrollo del proyecto de Ciencia de Datos enfocado en **Inside Airbnb** (optimización de precios, factores de éxito de anfitriones y análisis del mercado inmobiliario/turístico).

## 📁 Estructura del Proyecto

```
.
├── RECOMENDACIONES_ROADMAP.md      # Guía metodológica, fases y preguntas de negocio
├── README.md                       # Este archivo
├── data/
│   ├── selected/
│   │   └── airbnb/                 # Dataset principal (Inside Airbnb)
│   └── evaluation/
│       ├── olist/                  # Dataset de respaldo: E-commerce Brasil
│       └── lending_club/           # Dataset de respaldo: Riesgo Crediticio
├── notebooks/                      # Jupyter Notebooks organizados por fases
│   ├── 01_eda_calidad_datos.ipynb
│   ├── 02_limpieza_feature_engineering.ipynb
│   ├── 03_modelado_predictivo.ipynb
│   └── 04_interpretabilidad_negocio.ipynb
├── src/                            # Código fuente modular en Python
│   ├── __init__.py
│   ├── data_loader.py              # Funciones de descarga y carga de datos
│   ├── cleaning.py                 # Transformaciones y pipelines de limpieza
│   ├── features.py                 # Ingeniería de variables
│   └── models.py                   # Entrenamiento, evaluación y SHAP
└── reports/                        # Gráficas, reportes y métricas de impacto
```

## 🚀 Inicio Rápido

1. Consulta [RECOMENDACIONES_ROADMAP.md](file:///Users/jyarar/projects/u/x-semestre/data-science/RECOMENDACIONES_ROADMAP.md) para ver la justificación de datasets y el plan de 6 fases.
2. Descarga los datos de Inside Airbnb para la ciudad seleccionada en `data/selected/airbnb/raw/`.
3. Inicia la Fase 2 con el notebook de auditoría de calidad y EDA.
