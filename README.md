# 📞 Proyecto de Automatización de Evaluación de Llamadas con Python + Power BI

Construcción de una solución End-to-End para la **automatización de evaluación de calidad de llamadas telefónicas**, utilizando **Python** para el procesamiento de transcripciones y enriquecimiento de datos, y **Power BI** para la visualización analítica e interactiva de resultados.

Este proyecto contempla:

- Procesamiento y análisis de transcripciones de llamadas.
- Detección automática de atributos de calidad mediante reglas de negocio.
- Integración de fuentes complementarias como tipificaciones, dotación y tráfico.
- Construcción de un dataset analítico final listo para consumo.
- Desarrollo de un **dashboard interactivo en Power BI** orientado a calidad, desempeño operativo y seguimiento por agente/supervisor.

> **Nota:** Los datos incluidos en este repositorio son sintéticos y fueron generados con fines de demostración y portafolio.

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

# 📋 Requerimientos del Reporte

El dashboard fue diseñado para responder los siguientes requerimientos funcionales y analíticos del caso de uso:

## 1. Evaluación automatizada de calidad de llamadas

- Procesar transcripciones de llamadas desde una fuente estructurada.
- Detectar automáticamente atributos clave de calidad a partir del texto de la interacción.
- Evaluar señales tanto del diálogo del agente como del cliente.
- Identificar posibles anomalías o repeticiones excesivas en la transcripción.
- Clasificar el motivo principal del contacto mediante reglas de negocio.

## 2. Vista general operacional y de calidad

- Mostrar indicadores clave del período seleccionado:
  - Llamadas Totales
  - Duración Promedio
  - Cumplimiento QA
  - Cumplimiento Error Crítico
  - Nota Final
  - Cliente Satisfecho
- Permitir seguimiento de tendencia diaria de llamadas y duración promedio.
- Analizar el desempeño semanal de la operación mediante nota final y duración.
- Identificar diferencias de desempeño por tipificación.
- Comparar resultados por tramo de antigüedad de los agentes.
- Visualizar ranking de agentes según nota final.

## 3. Vista de desempeño por ejecutivo

- Analizar el desempeño individual de cada ejecutivo.
- Mostrar contexto operacional del agente seleccionado:
  - supervisor
  - llamadas totales
  - duración promedio
  - nota final
  - cumplimiento de error crítico
- Comparar el desempeño del ejecutivo contra el promedio del equipo.
- Analizar el posicionamiento del ejecutivo dentro de una matriz de calidad vs volumen.
- Evaluar diferencias de desempeño entre supervisores.
- Identificar perfiles de alto volumen, alta calidad o bajo desempeño.

## 4. Interactividad y experiencia de usuario

- Incorporar segmentadores para filtrar el análisis por:
  - mes
  - semana
  - país
  - supervisor
  - agente
- Permitir análisis dinámico según el contexto seleccionado.
- Incluir tooltips personalizados para enriquecer la lectura de los visuales sin sobrecargar la página principal.
- Mantener una navegación simple e intuitiva orientada a lectura ejecutiva y análisis detallado.

## 5. Modelo analítico y reglas de negocio

- Consolidar en un único dataset final la información de transcripciones, tipificaciones, dotación y tráfico.
- Calcular métricas derivadas para análisis de calidad y operación.
- Priorizar la ausencia de error crítico dentro de la lógica de evaluación final.
- Construir un modelo reutilizable para reporting y monitoreo de desempeño.

---

# ⚙️ Funcionalidades implementadas en Power BI

El dashboard incorpora funcionalidades orientadas a mejorar la experiencia de análisis y la interpretación del desempeño:

- Modelo conectado al dataset final generado en Python.
- KPIs ejecutivos para monitoreo general de la operación.
- Segmentadores globales para navegación y filtrado del análisis.
- Visualizaciones comparativas por día, semana, tipificación, supervisor y antigüedad.
- Matriz de desempeño calidad vs volumen para análisis de posicionamiento de ejecutivos.
- Comparación del ejecutivo seleccionado frente al equipo.
- Tooltips personalizados con métricas adicionales por agente.
- Uso de medidas DAX para cálculo de:
  - Cumplimiento QA
  - Cumplimiento Error Crítico
  - Cliente Satisfecho
  - Nota Final

---

# 🧮 Métricas principales del reporte

Entre las métricas principales desarrolladas en el dashboard se encuentran:

- Llamadas Totales
- Duración Promedio (Min.)
- Cumplimiento QA
- Cumplimiento Error Crítico
- Cliente Satisfecho
- Nota Final
- Llamadas por tipificación
- Nota Final por agente
- Desempeño por supervisor
- Evolución de Nota Final por período
- Relación entre calidad y volumen por ejecutivo

---

# 🏗️ Arquitectura de la Solución

La solución está dividida en dos etapas principales en Python y una capa final de visualización en Power BI.

## 1. Scoring de transcripciones

En esta etapa se procesan las transcripciones de llamadas para identificar atributos clave de calidad y comportamiento del cliente.

**Principales tareas:**

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

**Principales tareas:**

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
- evaluación por supervisor.

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
```

---

# 🧩 Fuentes de Datos

## Fuente principal

La fuente principal corresponde a transcripciones de llamadas, con posibilidad de ser cargadas desde:

- archivo local CSV
- consulta a BigQuery

**Campos base esperados:**

- `conversation_id`
- `conn_id`
- `local_start_time`
- `call_date`
- `month`
- `agent_id`
- `duration_seconds`
- `channel`
- `service_area`
- `transcript_text`

## Fuentes auxiliares

Para enriquecer el análisis, el proyecto utiliza además:

- `tipifications.csv`
- `agent_roster.csv`
- `daily_traffic.csv`

Estas fuentes aportan información como:

- grupo y detalle de tipificación,
- reincidencia de contacto,
- nombre del agente,
- supervisor,
- país,
- antigüedad,
- no respuesta,
- corte de llamada,
- dirección de cierre de la interacción.

> **Nota:** Los nombres de columnas del dataset se mantienen en inglés para respetar la estructura original de la fuente y mantener consistencia a lo largo del pipeline y del modelo analítico.

---

# 🧠 Lógica de Evaluación de Calidad

El proyecto utiliza reglas de negocio basadas en detección de frases dentro de la transcripción.

## Atributos evaluados sobre el diálogo del agente

Se detectan señales como:

- `greeting`
- `data_validation`
- `empathy_courtesy`
- `diagnosis_probing`
- `hold_management`
- `closing`

## Atributos evaluados sobre el diálogo del cliente

Se detectan señales como:

- `customer_dissatisfaction`

## Otras variables derivadas

También se calculan:

- `silence_seconds`
- `anomaly_repetition`
- `main_contact_reason`

---

# 📊 Métricas Analíticas Principales

A partir del dataset enriquecido, se construyen las métricas principales del modelo.

## Quality Score

Resume el cumplimiento de 6 chequeos QA:

- `greeting`
- `data_validation`
- `empathy_courtesy`
- `diagnosis_probing`
- `hold_management`
- `closing`

Este puntaje se expresa en escala de 0 a 100.

## Flow Complete

Marca si la llamada cumplió el flujo mínimo esperado:

- saludo
- validación de datos
- cierre

## Critical Error Flag

Se considera error crítico cuando:

- el cliente presenta señales de insatisfacción,
- y además el agente no realiza un cierre correcto.

## Silence Percentage

Convierte los segundos de silencio detectados en porcentaje sobre la duración total de la llamada.

---

# 🖥️ Dashboard en Power BI

El dashboard fue diseñado para entregar una vista ejecutiva y operativa del desempeño de llamadas evaluadas.

## Página 1: Overview Operacional y de Calidad

Esta página resume el comportamiento general del período seleccionado.

**Incluye:**

- Llamadas Totales
- Duración Promedio (Min.)
- Cumplimiento QA
- Cumplimiento Error Crítico
- Nota Final
- Cliente Satisfecho
- evolución diaria de llamadas y duración promedio
- comportamiento semanal de nota final y duración
- análisis por tipificación
- ranking de agentes
- análisis por tramo de antigüedad

### Definición de KPIs

#### Cumplimiento QA

```DAX
Cumplimiento QA =
AVERAGE(Sabana_Telecom_Postpaid_Care[quality_score]) / 100
```

#### Cumplimiento Error Crítico

```DAX
Cumplimiento Error Crítico =
1 - DIVIDE(
    CALCULATE(
        COUNTROWS(Sabana_Telecom_Postpaid_Care),
        Sabana_Telecom_Postpaid_Care[critical_error_flag] = 1
    ),
    [Llamadas Totales]
)
```

#### Cliente Satisfecho

```DAX
% Cliente Satisfecho =
1 - DIVIDE(
    CALCULATE(
        COUNTROWS(Sabana_Telecom_Postpaid_Care),
        Sabana_Telecom_Postpaid_Care[customer_dissatisfaction] = 1
    ),
    [Llamadas Totales]
)
```

#### Nota Final

La **Nota Final** se construye como una ponderación entre cumplimiento QA y ausencia de error crítico:

- **40%** calidad QA
- **60%** cumplimiento de error crítico

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
```

Esta lógica busca reflejar que una llamada puede tener buen cumplimiento procedural, pero si presenta un error crítico, su evaluación final debe verse fuertemente afectada.

---

## Página 2: Desempeño por Ejecutivo

La segunda página permite profundizar el análisis individual y comparativo.

**Incluye:**

- ejecutivo seleccionado,
- supervisor seleccionado,
- llamadas totales,
- duración promedio,
- nota final,
- cumplimiento error crítico,
- tabla de desempeño de ejecutivos,
- matriz de calidad vs volumen,
- evolución del ejecutivo vs equipo,
- comparación de desempeño por supervisor.

Esta vista permite identificar:

- ejecutivos de alto volumen,
- ejecutivos con mejor calidad,
- dispersiones entre supervisores,
- diferencias entre desempeño individual y promedio del equipo.

---

# 🛠️ Tecnologías Utilizadas

- **Python**
- **pandas**
- **NumPy**
- **openpyxl**
- **Google BigQuery**
- **Power BI**
- **DAX**

Además, el proceso de scoring utiliza procesamiento paralelo para evaluar transcripciones de manera más eficiente.

---

# 📂 Estructura del Repositorio

```text
call-center-qa-automatizacion-python-power-bi/
│
├── scripts/
│   ├── 01_score_transcripts.py
│   └── 02_enrich_and_prepare_dataset.py
│
├── datasets/
│   ├── raw/
│   │   ├── sample_conversations.csv
│   │   ├── tipifications.csv
│   │   ├── agent_roster.csv
│   │   └── daily_traffic.csv
│   │
│   └── processed/
│       ├── scored_conversations.xlsx
│       └── final_conversation_dataset.xlsx
│
├── dashboard/
│   └── telecom_postpaid_care.pbix
│
├── documentos/
│   ├── imagenes/
│   │   ├── general.png
│   │   ├── ejecutivos.png
│   │   └── enfoque_matriz_tooltip.png
│   └── diccionario_datos.md
│
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

# ▶️ Cómo Ejecutar el Proyecto

## 1. Clonar el repositorio

```bash
git clone https://github.com/matijgd/call-center-qa-automatizacion-python-power-bi.git
cd call-center-qa-automatizacion-python-power-bi
```

## 2. Crear entorno virtual

```bash
python -m venv venv
```

## 3. Activar entorno virtual

### Windows

```bash
venv\Scripts\activate
```

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 5. Preparar archivos de entrada

Ubicar los archivos base en las rutas definidas del proyecto:

- `datasets/raw/sample_conversations.csv`
- `datasets/raw/tipifications.csv`
- `datasets/raw/agent_roster.csv`
- `datasets/raw/daily_traffic.csv`

## 6. Ejecutar scoring de transcripciones

```bash
python scripts/01_score_transcripts.py
```

## 7. Ejecutar enriquecimiento del dataset

```bash
python scripts/02_enrich_and_prepare_dataset.py
```

## 8. Abrir el dashboard en Power BI

Abrir el archivo `.pbix` y conectar el modelo al dataset final generado.

---

# ✅ Resultados Esperados

Este proyecto permite:

- transformar transcripciones en indicadores analíticos estructurados,
- estandarizar criterios de evaluación,
- monitorear señales de riesgo y calidad,
- comparar desempeño por agente y supervisor,
- construir una base reutilizable para reporting operacional.

---

# 🚀 Posibles Mejoras Futuras

- ampliar los diccionarios de detección de frases y reglas de evaluación,
- externalizar la configuración del scoring para hacer el proceso más flexible,
- incorporar validaciones automáticas de calidad de datos,
- habilitar exportación a formatos más eficientes para datasets de mayor volumen,
- complementar la lógica basada en frases clave con técnicas más avanzadas de análisis de texto,
- ampliar el dashboard con nuevas vistas de tendencia y segmentación.

---

# 📸 Capturas del Dashboard

## Página 1 - Overview Operacional y de Calidad

![General](documentos/imagenes/general.png)

## Página 2 - Desempeño por Ejecutivo

![Detalle Ejecutivo](documentos/imagenes/ejecutivos.png)

## Tooltips interactivos para brindar mayor información

![Tooltips](documentos/imagenes/enfoque_matriz_tooltip.png)

---

# 👨‍💻 Autor

**Matías González**  
Analista de Datos | SQL Server | Power BI | Python | Excel
