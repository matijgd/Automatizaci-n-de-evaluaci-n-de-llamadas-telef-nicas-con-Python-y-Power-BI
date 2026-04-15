Automatización de evaluación de llamadas telefónicas con Python y Power BI
Descripción del proyecto

Este proyecto presenta una solución end-to-end para automatizar la evaluación de calidad de llamadas telefónicas a partir de transcripciones, enriqueciendo la información con fuentes operacionales complementarias y visualizando los resultados en un dashboard interactivo en Power BI.

La solución busca transformar transcripciones de llamadas en un dataset analítico estructurado, con indicadores de cumplimiento QA, detección de error crítico, satisfacción del cliente, duración, silencio, tipificación y desempeño por agente/supervisor.

Nota: Los nombres de las columnas del dataset se mantienen en inglés, ya que así venían desde la fuente original y se conservaron para mantener consistencia en el pipeline de datos y en el modelo analítico.

Objetivo

Construir un flujo reproducible que permita:

procesar transcripciones de llamadas,
detectar automáticamente atributos de calidad,
enriquecer los registros con información adicional de tipificación, dotación y tráfico,
generar un dataset final listo para análisis,
y visualizar resultados en un dashboard orientado a gestión operativa y desempeño.
Problema de negocio

La evaluación manual de llamadas suele ser lenta, limitada en cobertura y difícil de escalar. Este proyecto propone una alternativa automatizada para convertir transcripciones en señales medibles de calidad, permitiendo monitorear el cumplimiento de atributos clave del proceso de atención y generar una vista consolidada para seguimiento operativo.

Solución propuesta

La solución se compone de dos etapas principales en Python y una capa de visualización en Power BI:

Scoring de transcripciones
Se leen transcripciones desde un archivo CSV o desde BigQuery, se normaliza el esquema y se aplican reglas de detección sobre el diálogo del agente y del cliente.
Enriquecimiento del dataset
El resultado del scoring se cruza con archivos auxiliares de tipificaciones, dotación de agentes y tráfico diario para construir un dataset analítico final.
Dashboard en Power BI
Sobre la tabla final se construyen KPIs, visualizaciones comparativas y análisis por agente, supervisor, tipificación y antigüedad.

La primera etapa detecta flags como greeting, data_validation, empathy_courtesy, diagnosis_probing, hold_management, closing, customer_dissatisfaction, silence_seconds, anomaly_repetition y main_contact_reason. La segunda etapa agrega campos calendario, realiza merges por conn_id y agent_id, y calcula silence_pct, flow_complete, quality_score y critical_error_flag.

Arquitectura general
Transcripciones (CSV / BigQuery)
            │
            ▼
01_score_transcripts.py
- Normalización de esquema
- Limpieza de texto
- Detección de atributos QA
- Detección de insatisfacción
- Detección de anomalías
- Asignación de motivo principal
            │
            ▼
scored_conversations.xlsx
            │
            ▼
02_enrich_and_prepare_dataset.py
- Merge con tipifications.csv
- Merge con agent_roster.csv
- Merge con daily_traffic.csv
- Cálculo de métricas analíticas
            │
            ▼
final_conversation_dataset.xlsx
            │
            ▼
Power BI Dashboard
Fuentes de datos

El pipeline considera una fuente principal de transcripciones y tres archivos auxiliares para enriquecimiento:

Fuente principal
sample_conversations.csv o consulta a BigQuery
Campos base esperados:
conversation_id
conn_id
local_start_time
call_date
month
agent_id
duration_seconds
channel
service_area
transcript_text
Fuentes auxiliares
tipifications.csv
agent_roster.csv
daily_traffic.csv

El segundo script selecciona explícitamente columnas como tipification_group, tipification_detail, repeat_contact_flag, agent_name, country, supervisor, agent_tenure_months, agent_no_answer, agent_hangup y call_end_direction para construir el dataset final.

Etapa 1: scoring de transcripciones

El script 01_score_transcripts.py realiza las siguientes tareas:

carga la fuente desde CSV o BigQuery,
estandariza nombres de columnas y tipos,
separa el diálogo del agente y del cliente,
aplica reglas de búsqueda de frases clave,
detecta anomalías por repetición o dominancia de tokens,
calcula segundos de silencio detectados dentro de la transcripción,
clasifica el motivo principal del contacto,
y exporta un archivo intermedio llamado scored_conversations.xlsx.
Atributos detectados

Los principales atributos detectados son:

greeting
data_validation
empathy_courtesy
diagnosis_probing
hold_management
closing
customer_dissatisfaction
silence_seconds
anomaly_repetition
main_contact_reason
Etapa 2: enriquecimiento del dataset

El script 02_enrich_and_prepare_dataset.py toma el archivo intermedio y lo enriquece con información operacional adicional.

Procesos principales
normalización de llaves (conn_id, agent_id),
incorporación de campos calendario,
cruces con tipificaciones, dotación y tráfico,
cálculo de porcentaje de silencio,
cálculo de cumplimiento de flujo,
cálculo de puntaje QA,
cálculo de error crítico,
y exportación del dataset final final_conversation_dataset.xlsx.
Variables analíticas derivadas

El dataset final incluye, entre otras, las siguientes variables:

silence_pct
flow_complete
quality_score
critical_error_flag
Lógica de quality_score

El puntaje de calidad resume el cumplimiento de 6 chequeos QA:

greeting
data_validation
empathy_courtesy
diagnosis_probing
hold_management
closing
Lógica de critical_error_flag

Se marca como error crítico cuando:

customer_dissatisfaction = 1
y closing = 0

Estas definiciones están implementadas directamente en el script de enriquecimiento.

Dashboard en Power BI

El dashboard está diseñado para analizar desempeño operativo y calidad de atención desde dos niveles: vista general y detalle por ejecutivo.

Página 1: overview operacional y de calidad

Esta página resume el desempeño general del período seleccionado e incluye:

Llamadas Totales
Duración Promedio (Min.)
Cumplimiento QA
Cumplimiento Error Crítico
Nota Final
Cliente Satisfecho
tendencia diaria de llamadas y duración,
evolución semanal de nota final y duración,
análisis por tipificación,
ranking de agentes,
y análisis por tramo de antigüedad.

KPIs principales

Cumplimiento QA
Cumplimiento QA =
AVERAGE(Sabana_Telecom_Postpaid_Care[quality_score]) / 100
Cumplimiento Error Crítico
Cumplimiento Error Crítico =
1 - DIVIDE(
    CALCULATE(
        COUNTROWS(Sabana_Telecom_Postpaid_Care),
        Sabana_Telecom_Postpaid_Care[critical_error_flag] = 1
    ),
    [Llamadas Totales]
)
Cliente Satisfecho
% Cliente Satisfecho =
1 - DIVIDE(
    CALCULATE(
        COUNTROWS(Sabana_Telecom_Postpaid_Care),
        Sabana_Telecom_Postpaid_Care[customer_dissatisfaction] = 1
    ),
    [Llamadas Totales]
)
Nota Final

La Nota Final se modeló como una columna calculada que pondera:

40% cumplimiento QA
60% cumplimiento de error crítico
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

Esta lógica busca que una llamada con error crítico tenga un impacto fuerte en la evaluación final, incluso si presenta buen cumplimiento de checklist QA.

Página 2: desempeño por ejecutivo

La segunda página permite profundizar el análisis por agente y supervisor.

Incluye:

ejecutivo seleccionado,
supervisor seleccionado,
llamadas totales del ejecutivo,
duración promedio,
nota final,
cumplimiento de error crítico,
tabla de desempeño de ejecutivos,
matriz de desempeño calidad vs volumen,
evolución mensual del ejecutivo vs equipo,
y comparación de desempeño por supervisor.

Esta vista permite identificar perfiles de alto volumen, agentes con mejor calidad, dispersiones entre supervisores y comportamiento comparativo del ejecutivo frente al promedio del equipo.

Principales reglas de negocio del proyecto
El análisis se basa en detección de frases dentro del diálogo del agente y del cliente.
La satisfacción del cliente se aproxima mediante detección de expresiones de insatisfacción.
El error crítico depende del cruce entre insatisfacción del cliente y ausencia de cierre correcto.
La nota final prioriza la ausencia de error crítico por sobre el cumplimiento procedimental puro.
Los nombres de columnas del dataset se conservan en inglés por consistencia con la fuente y con el contrato de datos del pipeline.
Tecnologías utilizadas
Python
pandas
NumPy
Google BigQuery
openpyxl
Power BI
DAX

Además, el procesamiento del scoring se apoya en ejecución paralela con ProcessPoolExecutor para evaluar transcripciones fila a fila de forma independiente.

Cómo ejecutar el proyecto
1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPO>
2. Crear entorno virtual
python -m venv venv
3. Activar entorno virtual

Windows

venv\Scripts\activate
4. Instalar dependencias
pip install -r requirements.txt
5. Preparar archivos de entrada

Ubicar los archivos requeridos en las rutas correspondientes:

sample_conversations.csv o configurar variables para BigQuery
tipifications.csv
agent_roster.csv
daily_traffic.csv
6. Ejecutar scoring de transcripciones
python 01_score_transcripts.py
7. Ejecutar enriquecimiento del dataset
python 02_enrich_and_prepare_dataset.py
8. Abrir el dashboard en Power BI

Cargar el archivo .pbix del proyecto y conectar el modelo al dataset final generado.

Resultados del proyecto

Este proyecto permite:

convertir transcripciones en métricas analíticas estructuradas,
estandarizar criterios de evaluación,
monitorear calidad y riesgo operativo,
comparar desempeño por agente y supervisor,
y construir una base reusable para reporting de experiencia cliente y calidad de atención.
Alcances y consideraciones
Este proyecto tiene fines de portafolio.
La lógica de evaluación se basa en reglas y frases clave, por lo que puede evolucionar hacia enfoques más avanzados de NLP.
Para publicación en GitHub, se recomienda usar datos anonimizados o de ejemplo.
El modelo está pensado para ser escalable y fácilmente adaptable a nuevas reglas de scoring o nuevas fuentes de enriquecimiento.
Próximas mejoras posibles
incorporar diccionarios más amplios de detección,
parametrizar reglas en archivos externos,
mover la configuración a variables de entorno o archivos .env,
agregar pruebas automáticas,
exportar salidas también a CSV/Parquet,
incorporar una capa de validación de calidad de datos,
y ampliar el dashboard con vistas adicionales de tendencias y segmentación.
Autor

Matías González
Data Analyst | SQL Server | Power BI | Python | Excel

Capturas del dashboard

Reemplazar estas rutas por las imágenes definitivas dentro del repositorio.

![Overview](docs/images/dashboard_overview.png)
![Detalle ejecutivo](docs/images/dashboard_agent_detail.png)
