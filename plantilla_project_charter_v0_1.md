# Project Charter V0.1

## Nombre provisional del proyecto
**Modelo Predictivo y de Inteligencia de Mercado para la Optimización de Precios y Factores de Competitividad en Alojamiento Turístico (Inside Airbnb NYC)**

---
## 1. Dominio
¿En qué contexto existe el problema?

**Respuesta:**  
El proyecto se enmarca en el sector de **alojamiento turístico y plataformas de alquiler temporal (*Short-Term Rentals / Hospitality & PropTech*)** dentro de la economía colaborativa. Se centra en el análisis del mercado inmobiliario y turístico de grandes metrópolis (caso de estudio: **Nueva York**), caracterizado por una alta densidad de oferta, heterogeneidad en las características de los inmuebles, variabilidad estacional y estrictas dinámicas regulatorias locales.

---
## 2. Problema
¿Qué situación queremos comprender, analizar o resolver?

**Respuesta:**  
La fijación empírica o intuitiva de precios por parte de los anfitriones genera ineficiencias críticas de mercado:
1. **Subvaloración (*Underpricing*)**: Pérdida de ingresos potenciales al cobrar tarifas inferiores al valor real de mercado y sus comodidades.
2. **Sobreprecio (*Overpricing*)**: Reducción drástica en la tasa de ocupación y penalización en posicionamiento dentro de la plataforma.
3. **Opacidad en el retorno de comodidades (*Amenities ROI*)**: Desconocimiento sobre qué atributos físicos o servicios adicionales (e.g., aire acondicionado, espacio de trabajo, cocina, estacionamiento) justifican un incremento marginal cuantificable en la tarifa diaria.
4. **Falta de cuantificación del factor de micro-localización**: Dificultad para aislar el valor intrínseco del inmueble frente a su proximidad a distritos clave y atractivos turísticos.

---
## 3. Stakeholders potenciales
¿Quién necesita, utiliza, produce o puede verse afectado?

**Respuesta:**  
- **Anfitriones y Propietarios individuales (*Hosts*)**: Necesitan una guía cuantitativa y objetiva para fijar tarifas competitivas y priorizar inversiones en equipamiento.
- **Gestores de Propiedades e Inversionistas Inmobiliarios (*Property Managers*)**: Requieren modelos analíticos para evaluar la rentabilidad esperada, flujos de caja y viabilidad de activos en alquiler vacacional o de media estancia.
- **Huéspedes / Turistas**: Se benefician de un mercado con precios transparentes y proporcionales a la calidad, ubicación y servicios ofrecidos.
- **Plataformas de Intermediación**: Interesadas en maximizar la liquidez del mercado y la tasa de conversión reserva/visita.
- **Entidades de Turismo y Planificación Urbana**: Interesadas en comprender la distribución espacial de la oferta y su impacto en la dinámica de la vivienda.

---
## 4. Objetivo general
¿Qué pretendemos conseguir?

**Respuesta:**  
Desarrollar un sistema analítico y modelo predictivo (*Dynamic Pricing*) fundamentado en Machine Learning (LightGBM, XGBoost, Random Forest, Ridge) e interpretabilidad (SHAP) que permita estimar con precisión el precio óptimo por noche de los alojamientos turísticos en función de sus características estructurales, comodidades y ubicación geográfica, proporcionando explicabilidad sobre las palancas clave que impulsan el valor en el mercado.

---
## 5. Preguntas analíticas
1. **¿Cuál es el precio base óptimo estimado por noche** para una propiedad en función de su capacidad de huéspedes, número de habitaciones/baños y tipología de alojamiento (*Entire home/apt*, *Private room*, etc.)?
2. **¿Qué comodidades específicas (*amenities*)** generan el mayor incremento marginal en la tarifa diaria y cuáles no aportan un valor significativo al precio?
3. **¿Cómo influye la proximidad geográfica** a puntos de interés turístico e hitos clave (Times Square, Central Park, Financial District, Brooklyn Bridge) en el valor del alojamiento frente a atributos internos de la vivienda?
4. **¿Existen patrones diferenciados de valoración y dispersión de precios** entre los distintos distritos (*boroughs*) de la ciudad (Manhattan, Brooklyn, Queens, Bronx, Staten Island)?
5. **¿Qué características operativas y de reputación del anfitrión** (tiempo de respuesta, condición de *Superhost*, volumen y puntaje de reseñas) impactan de manera medible en la tarifa y competitividad del listado?

---
## 6. Fuente potencial de datos
**Fuente:** Inside Airbnb Open Datasets (Listings detallados, Reviews, Calendar y GeoJSON)  
**Institución:** Inside Airbnb (Iniciativa comunitaria independiente de auditoría de datos abiertos)  
**URL:** [https://insideairbnb.com/get-the-data/](https://insideairbnb.com/get-the-data/)

---
## 7. Criterio inicial de éxito
¿Qué tendría que producir el proyecto para considerarlo útil?

**Respuesta:**  
- **Criterio Técnico / Modelado:**
  - Superar sustancialmente al modelo base de referencia (*Baseline de Mediana*, MAE ≈ $90+ USD).
  - Alcanzar un coeficiente de determinación $R^2 \ge 0.65$ en escala real de dólares ($R^2 \ge 0.70$ en escala logarítmica) sobre un conjunto de prueba retenido (*test set* no visto).
  - Lograr un Error Absoluto Mediano ($MedAE$) inferior a **$30.00 USD** y un Error Absoluto Medio ($MAE$) inferior a **$45.00 USD**.
- **Criterio de Negocio y Explicabilidad:**
  - Implementar un módulo de interpretabilidad con valores **SHAP** (*Global & Local Summary / Feature Importance*) que jerarquice el impacto económico de las 10 características principales.
  - Proveer recomendaciones directas y reglas accionables para fijación de precios según distrito y comodidades.

---
## 8. Lo que todavía no sabemos
¿Qué comprobaremos durante Data Understanding?

**Respuesta:**  
1. **Proporción y tratamiento de valores atípicos (*outliers*)**: Rangos extremos de precio ($0 USD o > $5,000 USD/noche) y estancias mínimas atípicas (> 365 días) que requieran filtrado justificado.
2. **Impacto de la regulación local (Local Law 18 en NYC)**: Proporción de listados de corta estancia (< 30 días) vs. media/larga estancia (≥ 30 días) y cómo afecta la distribución de precios.
3. **Calidad y completitud de datos de anfitriones y reseñas**: Porcentaje de valores nulos en `host_response_time`, `review_scores_rating` y comportamiento de listados nuevos sin historial previo.
4. **Estructura y normalización del campo `amenities`**: Distribución de frecuencias de las comodidades (strings anidados en formato JSON crudo) y umbral de corte para binarización.
