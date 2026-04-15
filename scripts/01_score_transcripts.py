from pathlib import Path
import os
import re
import unicodedata
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from google.cloud import bigquery


# =========================================================
# CONFIGURACION GENERAL
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

# Opciones disponibles:
# - "csv": usa un archivo local de ejemplo o de trabajo
# - "bigquery": consulta una tabla en GCP
MODO_FUENTE = "csv"

# -------- CSV local --------
CSV_ENTRADA_LOCAL = os.getenv(
    "LOCAL_INPUT_CSV",
    str(BASE_DIR / "datasets" / "raw" / "sample_conversations.csv")
)

# -------- BigQuery --------
JSON_CUENTA_SERVICIO = os.getenv("SERVICE_ACCOUNT_JSON", "path/to/service_account.json")
ID_PROYECTO = os.getenv("PROJECT_ID", "portfolio-gcp-project")
ID_DATASET = os.getenv("DATASET_ID", "customer_support")
ID_TABLA = os.getenv("TABLE_ID", "conversation_transcripts")
FECHA_DESDE = os.getenv("DATE_FROM", "2025-01-01")
FECHA_HASTA = os.getenv("DATE_TO", "2025-01-31")

# -------- Salida --------
ARCHIVO_SALIDA = os.getenv(
    "OUTPUT_FILE",
    str(BASE_DIR / "datasets" / "processed" / "scored_conversations.xlsx")
)
# =========================================================
# REGLAS DE DETECCION
# =========================================================

# Estas listas se comparan contra el dialogo del agente o del cliente.
# Los nombres de columnas resultantes NO se traducen porque el segundo
# script depende de esos mismos nombres para continuar el flujo.
FRASES_SALUDO = [
    "buenos dias",
    "buenas tardes",
    "buenas noches",
    "gracias por comunicarte",
    "gracias por contactarte",
    "gracias por llamar",
    "bienvenido",
    "bienvenida",
]

FRASES_VALIDACION_DATOS = [
    "voy a validar sus datos",
    "voy a validar tus datos",
    "me confirma su rut",
    "me confirmas tu rut",
    "me confirma su numero",
    "me confirma su nombre",
    "necesito validar su identidad",
    "necesito corroborar su informacion",
]

FRASES_EMPATIAY_CORTESIA = [
    "entiendo tu molestia",
    "entiendo su molestia",
    "comprendo la situacion",
    "lamento lo ocurrido",
    "disculpe las molestias",
    "gracias por su paciencia",
    "gracias por tu paciencia",
]

FRASES_DIAGNOSTICO_Y_SONDEO = [
    "me puede indicar",
    "me puedes indicar",
    "desde cuando ocurre",
    "que mensaje le aparece",
    "que mensaje te aparece",
    "podria explicarme el problema",
    "voy a revisar el detalle",
]

FRASES_GESTION_ESPERA = [
    "permanezca en linea",
    "permanece en linea",
    "te pido unos segundos",
    "le pido unos segundos",
    "un momento por favor",
    "voy a revisar su caso",
]

FRASES_CIERRE = [
    "hay algo mas en que pueda ayudarle",
    "hay algo mas en que pueda ayudarte",
    "que tenga buen dia",
    "que tenga una buena tarde",
    "gracias por contactarnos",
    "gracias por comunicarse",
    "hasta luego",
]

FRASES_INSATISFACCION_CLIENTE = [
    "estoy molesto",
    "estoy molesta",
    "esto es una verguenza",
    "quiero dejar un reclamo",
    "no me solucionan nada",
    "llevo varios dias con el problema",
    "me siguen cobrando mal",
]

PATRONES_MOTIVO_PRINCIPAL = {
    "cobro incorrecto": "Billing",
    "me cobraron de mas": "Billing",
    "problema con la boleta": "Billing",
    "sin senal": "Technical Issue",
    "internet lento": "Technical Issue",
    "no funciona internet": "Technical Issue",
    "quiero cancelar": "Cancellation",
    "dar de baja": "Cancellation",
    "cambiar de plan": "Plan Change",
    "quiero portar": "Portability",
    "no puedo pagar": "Payment Issue",
    "estado de mi reclamo": "Claim Follow-up",
}


# =========================================================
# PARAMETROS DE CALIDAD DEL TEXTO
# =========================================================

UMBRAL_REPETICION_PALABRA = 10
UMBRAL_REPETICION_FRASE = 8
MINIMO_PALABRAS_FRASE = 4
UMBRAL_DOMINANCIA_TOKEN = 0.5


# =========================================================
# UTILIDADES
# =========================================================

def asegurar_carpeta(ruta: str) -> None:
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)


def normalizar_texto_comparable(texto: str) -> str:
    """Quita acentos para hacer comparaciones mas robustas."""
    texto = str(texto)
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(caracter for caracter in texto if not unicodedata.combining(caracter))


def limpiar_texto(texto: str) -> str:
    """Normaliza el texto para comparar frases y detectar repeticiones."""
    if pd.isna(texto):
        return ""

    texto = normalizar_texto_comparable(texto).lower()
    texto = re.sub(r"[\.,;:!?()\[\]{}\"\'\-]", " ", texto)
    texto = re.sub(r"\b\d{1,3}(?:[.,]\d{3})+\b", "NUM", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tiene_repeticion_excesiva_palabras(
    texto: str,
    umbral: int = UMBRAL_REPETICION_PALABRA,
) -> bool:
    """Detecta cuando una misma palabra aparece seguida muchas veces."""
    texto = limpiar_texto(texto)
    patron = r"\b(\S+)(?:\s+\1){" + str(umbral - 1) + r",}\b"
    return bool(re.search(patron, texto))


def tiene_frase_repetida(
    texto: str,
    minimo_palabras: int = MINIMO_PALABRAS_FRASE,
    umbral: int = UMBRAL_REPETICION_FRASE,
) -> bool:
    """Busca bloques de palabras que se repiten demasiadas veces."""
    texto = limpiar_texto(texto)
    palabras = texto.split()

    if len(palabras) < minimo_palabras * umbral:
        return False

    for indice in range(len(palabras) - minimo_palabras + 1):
        fragmento = " ".join(palabras[indice:indice + minimo_palabras])
        repeticiones = texto.count(fragmento)
        if repeticiones >= umbral:
            return True

    return False


def tiene_dominancia_de_tokens(
    texto: str,
    umbral: float = UMBRAL_DOMINANCIA_TOKEN,
) -> bool:
    """Marca anomalias cuando casi todo el texto esta dominado por un token."""
    texto = limpiar_texto(texto)
    tokens = texto.split()

    if not tokens:
        return False

    contador = Counter(tokens)
    apariciones_mas_comunes = contador.most_common(1)[0][1]
    return (apariciones_mas_comunes / len(tokens)) >= umbral


def detectar_anomalia_texto(texto: str) -> bool:
    """Agrupa las validaciones de ruido o repeticion anormal."""
    return (
        tiene_repeticion_excesiva_palabras(texto)
        or tiene_frase_repetida(texto)
        or tiene_dominancia_de_tokens(texto)
    )


def esta_cerca(
    frase_1: str,
    frase_2: str,
    texto: str,
    distancia_maxima: int = 50,
) -> bool:
    """Permite buscar dos frases cercanas dentro del mismo texto."""
    texto_minusculas = normalizar_texto_comparable(texto).lower()
    posicion_1 = texto_minusculas.find(normalizar_texto_comparable(frase_1).lower())
    posicion_2 = texto_minusculas.find(normalizar_texto_comparable(frase_2).lower())

    return (
        posicion_1 != -1
        and posicion_2 != -1
        and abs(posicion_1 - posicion_2) <= distancia_maxima
    )


def buscar_frases_en_dialogo(dialogo: str, frases: list[str]) -> int:
    """
    Devuelve 1 si encuentra alguna frase en el dialogo.
    Se conserva el formato 0/1 porque luego se usa para KPIs.
    """
    dialogo_minusculas = normalizar_texto_comparable(dialogo).lower()

    for frase in frases:
        if "near" in frase:
            partes = frase.split("near")
            if len(partes) == 2:
                izquierda = partes[0].strip().replace('"', "")
                derecha = partes[1].strip().replace('"', "")
                if esta_cerca(izquierda, derecha, dialogo_minusculas):
                    return 1
        elif normalizar_texto_comparable(frase).lower() in dialogo_minusculas:
            return 1

    return 0


def asignar_motivo_principal(texto: str, patrones: dict[str, str]) -> str:
    """Asigna una categoria simple segun frases clave detectadas."""
    texto_minusculas = normalizar_texto_comparable(texto).lower()

    for frase, motivo in patrones.items():
        if normalizar_texto_comparable(frase).lower() in texto_minusculas:
            return motivo

    return "Other"


def calcular_segundos_silencio_agente(texto_transcripcion: str) -> int:
    """Extrae el total de silencio/hold cuando viene incrustado en el texto."""
    coincidencia = re.search(
        r"Total de silencio/hold detectado:\s*(\d+):(\d+)",
        str(texto_transcripcion),
    )
    if coincidencia:
        minutos = int(coincidencia.group(1))
        segundos = int(coincidencia.group(2))
        return minutos * 60 + segundos
    return 0


def extraer_dialogo_agente(texto_transcripcion: str) -> str:
    """Separa unicamente las lineas dichas por el agente."""
    lineas = str(texto_transcripcion).split("\n")
    lineas_agente = []

    for linea in lineas:
        linea_limpia = linea.strip()
        if linea_limpia.lower().startswith("agente:") or linea_limpia.lower().startswith("agent:"):
            lineas_agente.append(linea_limpia.split(":", 1)[-1].strip())

    return " ".join(lineas_agente)


def extraer_dialogo_cliente(texto_transcripcion: str) -> str:
    """Separa unicamente las lineas dichas por el cliente."""
    lineas = str(texto_transcripcion).split("\n")
    lineas_cliente = []

    for linea in lineas:
        linea_limpia = linea.strip()
        if linea_limpia.lower().startswith("cliente:") or linea_limpia.lower().startswith("customer:"):
            lineas_cliente.append(linea_limpia.split(":", 1)[-1].strip())

    return " ".join(lineas_cliente)


def normalizar_esquema_salida(df: pd.DataFrame) -> pd.DataFrame:
    """
    Asegura las columnas minimas que necesita el segundo script.
    Ojo: los nombres de columnas se mantienen en ingles para no romper
    la integracion con los CSV ni con el paso siguiente del pipeline.
    """
    df.columns = df.columns.str.strip()

    mapa_renombres = {
        "call_id": "conversation_id",
        "id_conversation": "conversation_id",
        "id": "conversation_id",
        "connid": "conn_id",
        "agent": "agent_id",
        "duration": "duration_seconds",
        "skill_name": "service_area",
        "skill": "service_area",
        "start_time": "local_start_time",
        "processed_at": "local_start_time",
    }

    df = df.rename(columns=mapa_renombres)

    columnas_requeridas_con_default = {
        "conversation_id": None,
        "conn_id": None,
        "local_start_time": None,
        "call_date": None,
        "month": None,
        "agent_id": None,
        "duration_seconds": None,
        "channel": "Voice",
        "service_area": "Customer Support",
        "transcript_text": None,
    }

    for columna, valor_default in columnas_requeridas_con_default.items():
        if columna not in df.columns:
            df[columna] = valor_default

    # Si no viene conversation_id, intentamos heredarlo desde conn_id.
    # Como ultimo recurso, generamos uno secuencial para no dejar filas huerfanas.
    if df["conversation_id"].isna().all():
        if df["conn_id"].notna().any():
            df["conversation_id"] = df["conn_id"]
        else:
            df["conversation_id"] = [f"conv_{indice + 1}" for indice in range(len(df))]

    # Estandarizamos tipos para evitar fallos en filtros, merges y exportacion.
    df["conn_id"] = df["conn_id"].astype(str).str.strip()
    df["agent_id"] = df["agent_id"].astype(str).str.strip()
    df["channel"] = df["channel"].fillna("Voice").astype(str).str.strip()
    df["service_area"] = df["service_area"].fillna("Customer Support").astype(str).str.strip()
    df["transcript_text"] = df["transcript_text"].fillna("").astype(str)

    df["call_date"] = pd.to_datetime(df["call_date"], errors="coerce")
    df["local_start_time"] = pd.to_datetime(df["local_start_time"], errors="coerce")

    # Si falta la fecha/hora local, la heredamos desde la fecha de llamada.
    df["local_start_time"] = df["local_start_time"].fillna(df["call_date"])

    # Si no existe month, la derivamos desde call_date para el resto del flujo.
    if df["month"].isna().all():
        df["month"] = df["call_date"].dt.to_period("M").astype(str)

    return df


def guardar_salida(df: pd.DataFrame, archivo_salida: str) -> None:
    """Guarda el resultado final en Excel creando la carpeta si hace falta."""
    asegurar_carpeta(archivo_salida)

    for columna in df.select_dtypes(include=["datetime64[ns, UTC]", "datetime64[ns]"]).columns:
        try:
            df[columna] = df[columna].dt.tz_localize(None)
        except TypeError:
            pass

    df.to_excel(archivo_salida, index=False, engine="openpyxl")


# =========================================================
# PROCESAMIENTO POR REGISTRO
# =========================================================

def procesar_registro_transcripcion(registro: dict) -> dict:
    """
    Calcula las banderas y metricas de una transcripcion.
    Esta funcion se ejecuta por fila y por eso conviene mantenerla clara
    y autocontenida para el procesamiento en paralelo.
    """
    texto_transcripcion = str(registro.get("transcript_text", ""))

    dialogo_agente = extraer_dialogo_agente(texto_transcripcion)
    dialogo_cliente = extraer_dialogo_cliente(texto_transcripcion)

    return {
        "greeting": buscar_frases_en_dialogo(dialogo_agente, FRASES_SALUDO),
        "data_validation": buscar_frases_en_dialogo(dialogo_agente, FRASES_VALIDACION_DATOS),
        "empathy_courtesy": buscar_frases_en_dialogo(dialogo_agente, FRASES_EMPATIAY_CORTESIA),
        "diagnosis_probing": buscar_frases_en_dialogo(dialogo_agente, FRASES_DIAGNOSTICO_Y_SONDEO),
        "hold_management": buscar_frases_en_dialogo(dialogo_agente, FRASES_GESTION_ESPERA),
        "closing": buscar_frases_en_dialogo(dialogo_agente, FRASES_CIERRE),
        "customer_dissatisfaction": buscar_frases_en_dialogo(
            dialogo_cliente,
            FRASES_INSATISFACCION_CLIENTE,
        ),
        "silence_seconds": calcular_segundos_silencio_agente(texto_transcripcion),
        "anomaly_repetition": int(detectar_anomalia_texto(texto_transcripcion)),
        "main_contact_reason": asignar_motivo_principal(
            texto_transcripcion,
            PATRONES_MOTIVO_PRINCIPAL,
        ),
    }


# =========================================================
# EXTRACCION DE DATOS
# =========================================================

def consultar_bigquery() -> pd.DataFrame:
    """Consulta la fuente remota y devuelve un DataFrame estandarizado."""
    cliente = bigquery.Client.from_service_account_json(JSON_CUENTA_SERVICIO)

    consulta = f"""
    SELECT
        CAST(conversation_id AS STRING) AS conversation_id,
        CAST(conn_id AS STRING) AS conn_id,
        DATETIME(call_date) AS local_start_time,
        DATE(call_date) AS call_date,
        FORMAT_DATE('%Y-%m', DATE(call_date)) AS month,
        CAST(agent_id AS STRING) AS agent_id,
        CAST(duration_seconds AS INT64) AS duration_seconds,
        CAST(channel AS STRING) AS channel,
        CAST(service_area AS STRING) AS service_area,
        CAST(transcript_text AS STRING) AS transcript_text
    FROM `{ID_PROYECTO}.{ID_DATASET}.{ID_TABLA}`
    WHERE transcript_text IS NOT NULL
      AND DATE(call_date) BETWEEN '{FECHA_DESDE}' AND '{FECHA_HASTA}'
    """

    return cliente.query(consulta).result().to_dataframe()


def cargar_datos_fuente() -> pd.DataFrame:
    """Carga la fuente elegida y unifica el esquema base esperado."""
    if MODO_FUENTE == "bigquery":
        df = consultar_bigquery()
    elif MODO_FUENTE == "csv":
        df = pd.read_csv(CSV_ENTRADA_LOCAL)
    else:
        raise ValueError("MODO_FUENTE debe ser 'csv' o 'bigquery'.")

    return normalizar_esquema_salida(df)


def principal() -> None:
    print("Cargando datos fuente...")
    df = cargar_datos_fuente()

    print("Procesando transcripciones...")
    registros = df.to_dict(orient="records")

    # Se usa multiprocessing porque cada fila puede evaluarse de manera independiente.
    with ProcessPoolExecutor() as ejecutor:
        resultados = list(ejecutor.map(procesar_registro_transcripcion, registros))

    df_resultados = pd.DataFrame(resultados)
    df_final = pd.concat([df.reset_index(drop=True), df_resultados], axis=1)

    # Se mantiene este orden para que el script 2 reciba una estructura consistente.
    columnas_finales = [
        "conversation_id",
        "conn_id",
        "local_start_time",
        "call_date",
        "month",
        "agent_id",
        "duration_seconds",
        "channel",
        "service_area",
        "transcript_text",
        "greeting",
        "data_validation",
        "empathy_courtesy",
        "diagnosis_probing",
        "hold_management",
        "closing",
        "customer_dissatisfaction",
        "silence_seconds",
        "anomaly_repetition",
        "main_contact_reason",
    ]

    columnas_existentes = [columna for columna in columnas_finales if columna in df_final.columns]
    df_final = df_final[columnas_existentes]

    print("Guardando salida...")
    guardar_salida(df_final, ARCHIVO_SALIDA)

    print(f"Archivo generado correctamente: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    principal()
