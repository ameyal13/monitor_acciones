# indicadores.py - Cálculo de indicadores técnicos

import pandas as pd
import yfinance as yf
import config

def obtener_datos(simbolo):
    """Descarga datos históricos de una acción."""
    ticker = yf.Ticker(simbolo)
    df = ticker.history(
        period=config.PERIODO_HISTORICO,
        interval=config.INTERVALO_DATOS
    )
    return df

def calcular_medias_moviles(df):
    """Calcula media móvil corta y larga."""
    df["media_corta"] = df["Close"].rolling(window=config.MEDIA_CORTA).mean()
    df["media_larga"] = df["Close"].rolling(window=config.MEDIA_LARGA).mean()
    return df

def calcular_rsi(df):
    """Calcula el RSI."""
    delta = df["Close"].diff()
    ganancia = delta.where(delta > 0, 0).rolling(window=config.RSI_PERIODO).mean()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=config.RSI_PERIODO).mean()
    rs = ganancia / perdida
    df["rsi"] = 100 - (100 / (1 + rs))
    return df

def calcular_macd(df):
    """Calcula el MACD y su línea de señal."""
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_senal"] = df["macd"].ewm(span=9, adjust=False).mean()
    return df

def calcular_bollinger(df):
    """Calcula las bandas de Bollinger."""
    media = df["Close"].rolling(window=20).mean()
    std = df["Close"].rolling(window=20).std()
    df["bollinger_alta"] = media + (std * 2)
    df["bollinger_baja"] = media - (std * 2)
    df["bollinger_media"] = media
    return df

def calcular_soporte_resistencia(df):
    """Calcula soporte y resistencia de los últimos 5 días."""
    soporte = round(df["Low"].min(), 2)
    resistencia = round(df["High"].max(), 2)
    return soporte, resistencia

def calcular_volumen(df):
    """Verifica si el volumen actual está por encima del promedio."""
    promedio_volumen = df["Volume"].rolling(window=20).mean()
    df["volumen_alto"] = df["Volume"] > promedio_volumen
    return df

def contar_confirmaciones(ultima, anterior):
    """
    Cuenta cuántas confirmaciones hay para una señal de COMPRA.
    Máximo 5 confirmaciones.
    """
    confirmaciones = 0

    # 1. Cruce de medias hacia arriba
    if (anterior["media_corta"] <= anterior["media_larga"] and
            ultima["media_corta"] > ultima["media_larga"]):
        confirmaciones += 1

    # 2. RSI en zona saludable (no sobrecomprado ni sobrevendido)
    if 40 <= ultima["rsi"] <= 65:
        confirmaciones += 1

    # 3. Volumen por encima del promedio
    if ultima["volumen_alto"]:
        confirmaciones += 1

    # 4. MACD cruzando hacia arriba
    if (anterior["macd"] <= anterior["macd_senal"] and
            ultima["macd"] > ultima["macd_senal"]):
        confirmaciones += 1

    # 5. Precio cerca de la banda baja de Bollinger (precio "barato")
    rango = ultima["bollinger_alta"] - ultima["bollinger_baja"]
    if rango > 0:
        posicion = (ultima["Close"] - ultima["bollinger_baja"]) / rango
        if posicion <= 0.35:
            confirmaciones += 1

    return confirmaciones

def contar_confirmaciones_venta(ultima, anterior):
    """
    Cuenta confirmaciones para señal de VENTA.
    """
    confirmaciones = 0

    # 1. Cruce de medias hacia abajo
    if (anterior["media_corta"] >= anterior["media_larga"] and
            ultima["media_corta"] < ultima["media_larga"]):
        confirmaciones += 1

    # 2. RSI en zona de sobrecompra
    if ultima["rsi"] >= 65:
        confirmaciones += 1

    # 3. Volumen por encima del promedio
    if ultima["volumen_alto"]:
        confirmaciones += 1

    # 4. MACD cruzando hacia abajo
    if (anterior["macd"] >= anterior["macd_senal"] and
            ultima["macd"] < ultima["macd_senal"]):
        confirmaciones += 1

    # 5. Precio cerca de la banda alta de Bollinger (precio "caro")
    rango = ultima["bollinger_alta"] - ultima["bollinger_baja"]
    if rango > 0:
        posicion = (ultima["Close"] - ultima["bollinger_baja"]) / rango
        if posicion >= 0.65:
            confirmaciones += 1

    return confirmaciones

def generar_senal(df):
    """
    Determina señal de compra, venta o neutro
    basándose en mínimo 3 confirmaciones de 5.
    """
    ultima = df.iloc[-1]
    anterior = df.iloc[-2]

    confirmaciones_compra = contar_confirmaciones(ultima, anterior)
    confirmaciones_venta = contar_confirmaciones_venta(ultima, anterior)

    soporte, resistencia = calcular_soporte_resistencia(df)

    if confirmaciones_compra >= 3:
        senal = "COMPRA"
        confirmaciones = confirmaciones_compra
    elif confirmaciones_venta >= 3:
        senal = "VENTA"
        confirmaciones = confirmaciones_venta
    else:
        senal = "NEUTRO"
        confirmaciones = max(confirmaciones_compra, confirmaciones_venta)

    return (
        senal,
        round(ultima["rsi"], 2),
        round(ultima["Close"], 2),
        confirmaciones,
        soporte,
        resistencia
    )

def procesar_accion(simbolo):
    """Función principal que orquesta todo el análisis."""
    df = obtener_datos(simbolo)

    if df.empty or len(df) < 30:
        return None

    df = calcular_medias_moviles(df)
    df = calcular_rsi(df)
    df = calcular_macd(df)
    df = calcular_bollinger(df)
    df = calcular_volumen(df)
    df = df.dropna()

    if len(df) < 2:
        return None

    senal, rsi, precio, confirmaciones, soporte, resistencia = generar_senal(df)

    return {
        "simbolo": simbolo,
        "precio": precio,
        "rsi": rsi,
        "senal": senal,
        "confirmaciones": confirmaciones,
        "soporte": soporte,
        "resistencia": resistencia
    }