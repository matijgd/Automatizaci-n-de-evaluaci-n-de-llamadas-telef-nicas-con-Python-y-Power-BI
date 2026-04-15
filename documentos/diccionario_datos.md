# 📘 Diccionario de Datos

Este documento describe los principales archivos y campos utilizados en el proyecto de automatización de evaluación de llamadas.

> **Nota:** Los nombres de columnas se mantienen en inglés para respetar la estructura original de la fuente y mantener consistencia en el pipeline de datos.

---

# 1. Archivos principales del proyecto

## `sample_conversations.csv`
Archivo base de transcripciones de llamadas utilizado como fuente principal del proceso de scoring.

## `tipifications.csv`
Archivo auxiliar con información de tipificación de la llamada.

## `agent_roster.csv`
Archivo auxiliar con información de dotación de agentes, supervisores, país y antigüedad.

## `daily_traffic.csv`
Archivo auxiliar con información operacional de tráfico y cierre de llamada.

## `scored_conversations.xlsx`
Salida intermedia generada por el script `01_score_transcripts.py`, que incorpora atributos detectados sobre la transcripción.

## `final_conversation_dataset.xlsx`
Dataset final generado por el script `02_enrich_and_prepare_dataset.py`, utilizado como fuente del dashboard en Power BI.

---

# 2. Diccionario de campos del dataset final

## Identificación y contexto de la llamada

| Campo | Descripción |
|------|-------------|
| `conversation_id` | Identificador único de la conversación. |
| `conn_id` | Identificador de conexión o interacción utilizado para cruces entre tablas. |
| `local_start_time` | Fecha y hora de inicio local de la llamada. |
| `call_date` | Fecha de la llamada. |
| `date` | Fecha derivada para análisis diario. |
| `month` | Mes de la llamada en formato período. |
| `week` | Semana calendario derivada de la fecha de llamada. |
| `channel` | Canal de atención. |
| `service_area` | Área o servicio asociado a la llamada. |

---

## Información del agente

| Campo | Descripción |
|------|-------------|
| `agent_id` | Identificador del agente. |
| `agent_name` | Nombre del agente. |
| `country` | País asociado al agente o la operación. |
| `supervisor` | Nombre del supervisor del agente. |
| `agent_tenure_months` | Antigüedad del agente en meses. |

---

## Variables operacionales de la llamada

| Campo | Descripción |
|------|-------------|
| `duration_seconds` | Duración total de la llamada en segundos. |
| `silence_seconds` | Segundos de silencio o espera detectados en la transcripción. |
| `silence_pct` | Porcentaje de silencio respecto a la duración total de la llamada. |
| `agent_no_answer` | Indicador de no respuesta del agente. |
| `agent_hangup` | Indicador de corte por parte del agente. |
| `call_end_direction` | Dirección o tipo de cierre de la llamada. |

---

## Tipificación y motivo de contacto

| Campo | Descripción |
|------|-------------|
| `main_contact_reason` | Motivo principal de contacto detectado a partir de reglas sobre el texto. |
| `tipification_group` | Grupo de tipificación de la llamada. |
| `tipification_detail` | Detalle específico de la tipificación. |
| `repeat_contact_flag` | Indicador de contacto reiterado o reincidencia. |

---

## Atributos de calidad detectados

| Campo | Descripción |
|------|-------------|
| `greeting` | Indicador de detección de saludo en el diálogo del agente. |
| `data_validation` | Indicador de validación de datos por parte del agente. |
| `empathy_courtesy` | Indicador de expresiones de empatía o cortesía. |
| `diagnosis_probing` | Indicador de diagnóstico o sondeo del problema. |
| `hold_management` | Indicador de correcta gestión de espera o silencio. |
| `closing` | Indicador de cierre de llamada. |
| `customer_dissatisfaction` | Indicador de insatisfacción detectada en el diálogo del cliente. |
| `anomaly_repetition` | Indicador de anomalías o repeticiones excesivas detectadas en el texto. |

> En general, estos campos funcionan como banderas binarias:
>
> - `1` = atributo detectado  
> - `0` = atributo no detectado

---

## Métricas derivadas

| Campo | Descripción |
|------|-------------|
| `flow_complete` | Indicador de cumplimiento del flujo mínimo esperado (saludo, validación y cierre). |
| `quality_score` | Puntaje de calidad calculado a partir del cumplimiento de atributos QA. |
| `critical_error_flag` | Indicador de error crítico cuando se detecta insatisfacción del cliente y ausencia de cierre correcto. |

---

## Texto fuente

| Campo | Descripción |
|------|-------------|
| `transcript_text` | Texto completo de la transcripción de la llamada. |

---

# 3. Reglas de negocio principales

## `quality_score`
Resume el cumplimiento de seis atributos QA:

- `greeting`
- `data_validation`
- `empathy_courtesy`
- `diagnosis_probing`
- `hold_management`
- `closing`

Se expresa en una escala de 0 a 100.

## `flow_complete`
Se marca con valor `1` cuando la llamada cumple simultáneamente con:

- saludo,
- validación de datos,
- cierre.

En caso contrario, toma valor `0`.

## `critical_error_flag`
Se marca con valor `1` cuando:

- `customer_dissatisfaction = 1`
- y `closing = 0`

En caso contrario, toma valor `0`.

---

# 4. Métrica utilizada en Power BI: Nota Final

La columna calculada **Nota Final** se construye en Power BI como una ponderación entre calidad QA y cumplimiento de error crítico:

- **40%** `quality_score`
- **60%** ausencia de error crítico

```DAX
Nota Final =
VAR CriticalErrorFix =
    IF(
        Sabana_Telecom_Postpaid_Care[critical_error_flag] = 1,
        0,
        100
    )
RETURN
    Sabana_Telecom_Postpaid_Care[quality_score] * 0.4 +
    CriticalErrorFix * 0.6
