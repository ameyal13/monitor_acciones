# notificaciones.py - Bot de Telegram

import asyncio
import telegram
import config

bot = telegram.Bot(token=config.TELEGRAM_TOKEN)

async def _enviar(mensaje):
    async with bot:
        await bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=mensaje,
            parse_mode="HTML"
        )

def enviar_mensaje(mensaje):
    """Función sincrónica que puede llamarse desde cualquier hilo."""
    try:
        asyncio.run(_enviar(mensaje))
    except Exception as e:
        print(f"[Telegram] Error enviando mensaje: {e}")

def mensaje_compra(simbolo, precio, rsi, confirmaciones, soporte, resistencia):
    texto = (
        f"🟢 <b>SEÑAL DE COMPRA</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📈 Acción: <b>{simbolo}</b>\n"
        f"💵 Precio: <b>${precio}</b>\n"
        f"📊 RSI: {rsi}\n"
        f"✅ Confirmaciones: {confirmaciones}/5\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔵 Soporte:     ${soporte}\n"
        f"🔴 Resistencia: ${resistencia}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )
    enviar_mensaje(texto)

def mensaje_venta(simbolo, precio_venta, precio_compra, rsi, confirmaciones):
    if precio_compra:
        diferencia = round(precio_venta - precio_compra, 2)
        porcentaje = round((diferencia / precio_compra) * 100, 2)
        if diferencia >= 0:
            resultado = f"🟢 Ganancia: +${diferencia} (+{porcentaje}%)"
        else:
            resultado = f"🔴 Pérdida: -${abs(diferencia)} ({porcentaje}%)"
        simulacion = (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧮 <b>Simulación del trade:</b>\n"
            f"   Compraste a:  ${precio_compra}\n"
            f"   Vendiste a:   ${precio_venta}\n"
            f"   {resultado}"
        )
    else:
        simulacion = ""

    texto = (
        f"🔴 <b>SEÑAL DE VENTA</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📉 Acción: <b>{simbolo}</b>\n"
        f"💵 Precio: <b>${precio_venta}</b>\n"
        f"📊 RSI: {rsi}\n"
        f"✅ Confirmaciones: {confirmaciones}/5\n"
        f"{simulacion}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )
    enviar_mensaje(texto)

def mensaje_analisis_ia(simbolo, analisis):
    texto = (
        f"🤖 <b>Análisis IA — {simbolo}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{analisis}"
    )
    enviar_mensaje(texto)