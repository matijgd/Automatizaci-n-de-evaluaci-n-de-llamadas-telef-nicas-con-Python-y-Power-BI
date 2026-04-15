# 📞 Proyecto de Automatización de Evaluación de Llamadas con Python + Power BI

Construcción de una solución End-to-End para la **automatización de evaluación de calidad de llamadas telefónicas**, utilizando **Python** para el procesamiento de transcripciones y enriquecimiento de datos, y **Power BI** para la visualización analítica e interactiva de resultados.

Este proyecto contempla:

- Procesamiento y análisis de transcripciones de llamadas.
- Detección automática de atributos de calidad mediante reglas de negocio.
- Integración de fuentes complementarias como tipificaciones, dotación y tráfico.
- Construcción de un dataset analítico final listo para consumo.
- Desarrollo de un **dashboard interactivo en Power BI** orientado a calidad, desempeño operativo y seguimiento por agente/supervisor.

---

# 📌 Descripción General del Proyecto

El objetivo de este proyecto es simular una solución moderna de analítica aplicada a operaciones de atención telefónica, cubriendo el flujo completo desde la transcripción de llamadas hasta la construcción de un reporte ejecutivo e interactivo.

**Flujo general del proyecto:**

**Transcripciones → Scoring automático → Enriquecimiento de datos → Dataset final → Dashboard en Power BI**

A nivel funcional, el proyecto permite:

- Estandarizar y procesar transcripciones provenientes de múltiples fuentes.
- Detectar automáticamente atributos relevantes de calidad en la interacción.
- Incorporar contexto operacional a través de cruces con otras tablas.
- Construir una base analítica reutilizable para reporting.
- Visualizar resultados mediante un dashboard orientado a gestión y desempeño.

---

# 🏗️ Arquitectura de la Solución

La solución está dividida en dos etapas principales en Python y una capa final de visualización en Power BI.

## 1. Scoring de transcripciones

En esta etapa se procesan las transcripciones de llamadas para identificar atributos clave de calidad y comportamiento del cliente.

Principales tareas:

- Carga de datos desde **CSV** o **BigQuery**.
- Normalización del esquema base.
- Separación del diálogo de agente y cliente.
- Limpieza y normalización de texto.
- Detección de frases clave.
- Cálculo de segundos de silencio.
- Detección de anomalías por repetición.
- Clasificación del motivo principal del contacto.

## 2. Enriquecimiento del dataset

Una vez calculadas las señales principales sobre la transcripción, el resultado se cruza con fuentes auxiliares para enriquecer el análisis.

Principales tareas:

- Normalización de llaves como `conn_id` y `agent_id`.
- Integración con tipificaciones, dotación y tráfico diario.
- Derivación de campos calendario.
- Cálculo de métricas analíticas finales.
- Generación del dataset consolidado para consumo en Power BI.

## 3. Visualización en Power BI

Sobre el dataset final se construye un dashboard orientado a:

- monitoreo de calidad,
- seguimiento operativo,
- análisis por tipificación,
- comparación de desempeño por ejecutivo,
- y evaluación por supervisor.

---

# ⚙️ Flujo de Datos del Proyecto

```text
Fuente principal de transcripciones (CSV / BigQuery)
                │
                ▼
01_score_transcripts.py
- Normalización de esquema
- Limpieza de texto
- Extracción de diálogo agente / cliente
- Detección de atributos QA
- Detección de insatisfacción
- Detección de anomalías
- Clasificación de motivo principal
                │
                ▼
scored_conversations.xlsx
                │
                ▼
02_enrich_and_prepare_dataset.py
- Cruce con tipifications.csv
- Cruce con agent_roster.csv
- Cruce con daily_traffic.csv
- Cálculo de métricas analíticas
                │
                ▼
final_conversation_dataset.xlsx
                │
                ▼
Dashboard Power BI
