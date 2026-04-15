from pathlib import Path
import os

import numpy as np
import pandas as pd


# =========================================================
# RUTAS DE ENTRADA Y SALIDA
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVO_ENTRADA_PUNTUADO = str(BASE_DIR / "datasets" / "processed" / "scored_conversations.xlsx")
ARCHIVO_TIPIFICACIONES = str(BASE_DIR / "datasets" / "raw" / "tipifications.csv")
ARCHIVO_DOTACION_AGENTES = str(BASE_DIR / "datasets" / "raw" / "agent_roster.csv")
ARCHIVO_TRAFICO_DIARIO = str(BASE_DIR / "datasets" / "raw" / "daily_traffic.csv")
ARCHIVO_SALIDA_FINAL = str(BASE_DIR / "datasets" / "processed" / "final_conversation_dataset.xlsx")


# =========================================================
# FUNCIONES DE APOYO
# =========================================================

def normalizar_clave_texto(serie: pd.Series) -> pd.Series:
    """Limpia espacios y unifica a minusculas claves como conn_id."""
    return serie.astype(str).str.strip().str.lower()


def normalizar_id_agente(serie: pd.Series) -> pd.Series:
    """
    Convierte ids como 123.0 en 123 para facilitar merges.
    Esto ayuda cuando el origen mezcla numeros, texto y nulos.
    """
    return serie.apply(
        lambda valor: str(int(valor)) if isinstance(valor, float) and not pd.isna(valor) else str(valor)
    ).str.strip()


def asegurar_carpeta(ruta: str) -> None:
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)


def agregar_campos_calendario(df: pd.DataFrame) -> pd.DataFrame:
    """Deriva columnas de fecha utiles para analisis posteriores."""
    df["call_date"] = pd.to_datetime(df["call_date"], errors="coerce")
    df["date"] = df["call_date"].dt.date
    df["month"] = df["call_date"].dt.to_period("M").astype(str)
    df["week"] = df["call_date"].dt.isocalendar().week.astype("Int64")
    return df


def calcular_puntaje_calidad(df: pd.DataFrame) -> pd.Series:
    """Resume el cumplimiento de chequeos de calidad en una escala 0-100."""
    columnas_calidad = [
        "greeting",
        "data_validation",
        "empathy_courtesy",
        "diagnosis_probing",
        "hold_management",
        "closing",
    ]
    return (df[columnas_calidad].fillna(0).sum(axis=1) / len(columnas_calidad) * 100).round(2)


def calcular_flujo_completo(df: pd.DataFrame) -> pd.Series:
    """
    Marca si el contacto cumple el flujo minimo esperado.
    En este caso se pide saludo, validacion y cierre.
    """
    columnas_requeridas = [
        "greeting",
        "data_validation",
        "closing",
    ]
    return np.where(df[columnas_requeridas].fillna(0).sum(axis=1) == len(columnas_requeridas), 1, 0)


def calcular_bandera_error_critico(df: pd.DataFrame) -> pd.Series:
    """
    Considera error critico cuando hubo insatisfaccion del cliente
    y ademas el agente no cerro correctamente la interaccion.
    """
    condiciones_criticas = (
        (df["customer_dissatisfaction"].fillna(0) == 1)
        & (df["closing"].fillna(0) == 0)
    )
    return np.where(condiciones_criticas, 1, 0)


def calcular_porcentaje_silencio(df: pd.DataFrame) -> pd.Series:
    """Convierte segundos de silencio en porcentaje sobre la duracion total."""
    duracion = pd.to_numeric(df["duration_seconds"], errors="coerce").fillna(0)
    silencio = pd.to_numeric(df["silence_seconds"], errors="coerce").fillna(0)
    return np.where(duracion > 0, (silencio / duracion * 100).round(2), 0)


def cargar_fuentes() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Lee todos los archivos base del pipeline."""
    df_puntuado = pd.read_excel(ARCHIVO_ENTRADA_PUNTUADO)
    df_tipificaciones = pd.read_csv(ARCHIVO_TIPIFICACIONES)
    df_dotacion = pd.read_csv(ARCHIVO_DOTACION_AGENTES)
    df_trafico = pd.read_csv(ARCHIVO_TRAFICO_DIARIO)
    return df_puntuado, df_tipificaciones, df_dotacion, df_trafico


def limpiar_nombres_columnas(dataframes: list[pd.DataFrame]) -> None:
    """Quita espacios en los encabezados para evitar errores silenciosos."""
    for df in dataframes:
        df.columns = df.columns.str.strip()


def seleccionar_columnas_necesarias(
    df_tipificaciones: pd.DataFrame,
    df_dotacion: pd.DataFrame,
    df_trafico: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Nos quedamos solo con las columnas utiles para el dataset final.
    Esto hace mas claro el merge y reduce duplicados innecesarios.
    """
    df_tipificaciones = df_tipificaciones[
        ["conn_id", "tipification_group", "tipification_detail", "repeat_contact_flag"]
    ].drop_duplicates(subset=["conn_id"])

    df_dotacion = df_dotacion[
        ["agent_id", "agent_name", "country", "supervisor", "agent_tenure_months"]
    ].drop_duplicates(subset=["agent_id"])

    df_trafico = df_trafico[
        ["conn_id", "agent_no_answer", "agent_hangup", "call_end_direction"]
    ].drop_duplicates(subset=["conn_id"])

    return df_tipificaciones, df_dotacion, df_trafico


def preparar_base_puntuada(df_puntuado: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza claves y agrega campos derivados sobre la tabla principal.
    Esta es la base sobre la que luego se unen las demas fuentes.
    """
    df_puntuado["conn_id"] = normalizar_clave_texto(df_puntuado["conn_id"])
    df_puntuado["agent_id"] = normalizar_id_agente(df_puntuado["agent_id"])
    df_puntuado = agregar_campos_calendario(df_puntuado)

    # Si el archivo intermedio no trae local_start_time, usamos call_date
    # para que el dataset final siempre tenga un timestamp base.
    if "local_start_time" not in df_puntuado.columns:
        df_puntuado["local_start_time"] = df_puntuado["call_date"]

    return df_puntuado


def preparar_tablas_relacionadas(
    df_tipificaciones: pd.DataFrame,
    df_dotacion: pd.DataFrame,
    df_trafico: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Normaliza las llaves de relacion antes de hacer los merges."""
    df_tipificaciones["conn_id"] = normalizar_clave_texto(df_tipificaciones["conn_id"])
    df_trafico["conn_id"] = normalizar_clave_texto(df_trafico["conn_id"])
    df_dotacion["agent_id"] = normalizar_id_agente(df_dotacion["agent_id"])

    return seleccionar_columnas_necesarias(df_tipificaciones, df_dotacion, df_trafico)


def enriquecer_dataset(
    df_puntuado: pd.DataFrame,
    df_tipificaciones: pd.DataFrame,
    df_dotacion: pd.DataFrame,
    df_trafico: pd.DataFrame,
) -> pd.DataFrame:
    """Une todas las fuentes y calcula las metricas finales."""
    df_final = df_puntuado.merge(
        df_tipificaciones,
        on="conn_id",
        how="left",
    )

    df_final = df_final.merge(
        df_dotacion,
        on="agent_id",
        how="left",
    )

    df_final = df_final.merge(
        df_trafico,
        on="conn_id",
        how="left",
    )

    df_final["silence_pct"] = calcular_porcentaje_silencio(df_final)
    df_final["flow_complete"] = calcular_flujo_completo(df_final)
    df_final["quality_score"] = calcular_puntaje_calidad(df_final)
    df_final["critical_error_flag"] = calcular_bandera_error_critico(df_final)

    # Estas banderas se completan con 0 porque la ausencia de dato en estas
    # tablas auxiliares se interpreta como "no ocurrio" para el analisis.
    df_final["agent_no_answer"] = df_final["agent_no_answer"].fillna(0).astype(int)
    df_final["agent_hangup"] = df_final["agent_hangup"].fillna(0).astype(int)
    df_final["repeat_contact_flag"] = df_final["repeat_contact_flag"].fillna(0).astype(int)

    return df_final


def ordenar_columnas_finales(df_final: pd.DataFrame) -> pd.DataFrame:
    """
    Mantiene un orden estable en el Excel final.
    Los nombres de columnas se dejan tal cual porque ya son parte del
    contrato de datos del proyecto.
    """
    columnas_finales = [
        "conversation_id",
        "conn_id",
        "local_start_time",
        "call_date",
        "date",
        "month",
        "week",
        "channel",
        "service_area",
        "agent_id",
        "agent_name",
        "country",
        "supervisor",
        "agent_tenure_months",
        "duration_seconds",
        "silence_seconds",
        "silence_pct",
        "main_contact_reason",
        "tipification_group",
        "tipification_detail",
        "repeat_contact_flag",
        "agent_no_answer",
        "agent_hangup",
        "call_end_direction",
        "greeting",
        "data_validation",
        "empathy_courtesy",
        "diagnosis_probing",
        "hold_management",
        "closing",
        "customer_dissatisfaction",
        "anomaly_repetition",
        "flow_complete",
        "quality_score",
        "critical_error_flag",
        "transcript_text",
    ]

    columnas_existentes = [columna for columna in columnas_finales if columna in df_final.columns]
    return df_final[columnas_existentes]


def guardar_dataset_final(df_final: pd.DataFrame) -> None:
    asegurar_carpeta(ARCHIVO_SALIDA_FINAL)
    df_final.to_excel(ARCHIVO_SALIDA_FINAL, index=False, engine="openpyxl")


def principal() -> None:
    print("Cargando archivos base...")
    df_puntuado, df_tipificaciones, df_dotacion, df_trafico = cargar_fuentes()

    limpiar_nombres_columnas([df_puntuado, df_tipificaciones, df_dotacion, df_trafico])

    print("Preparando tablas para el cruce...")
    df_puntuado = preparar_base_puntuada(df_puntuado)
    df_tipificaciones, df_dotacion, df_trafico = preparar_tablas_relacionadas(
        df_tipificaciones,
        df_dotacion,
        df_trafico,
    )

    print("Enriqueciendo dataset final...")
    df_final = enriquecer_dataset(df_puntuado, df_tipificaciones, df_dotacion, df_trafico)
    df_final = ordenar_columnas_finales(df_final)

    print("Guardando salida final...")
    guardar_dataset_final(df_final)

    print(f"Archivo final generado correctamente: {ARCHIVO_SALIDA_FINAL}")


if __name__ == "__main__":
    principal()
