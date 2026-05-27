# alertas.py - Manejo de alertas, eventos y notificaciones

import threading
import datetime
import monitor
import notificaciones
import analista
import config

def procesar_alertas():
    """
    Corre en un hilo separado.
    Espera a que el evento_alerta se active y procesa la cola.
    """
    print("[Alertas] Hilo de alertas iniciado.\n")

    while True:
        monitor.evento_alerta.wait()

        while not monitor.cola_resultados.empty():
            try:
                resultado = monitor.cola_resultados.get_nowait()
                simbolo      = resultado["simbolo"]
                precio       = resultado["precio"]
                rsi          = resultado["rsi"]
                senal        = resultado["senal"]
                confirmaciones = resultado["confirmaciones"]
                soporte      = resultado["soporte"]
                resistencia  = resultado["resistencia"]
                precio_compra = resultado.get("precio_compra", None)
                hora         = datetime.datetime.now().strftime("%H:%M:%S")

                # Imprimir en consola
                if senal == "COMPRA":
                    print(f"🟢 [{hora}] COMPRA  | {simbolo} | "
                          f"${precio} | RSI: {rsi} | "
                          f"Confirmaciones: {confirmaciones}/5")
                elif senal == "VENTA":
                    print(f"🔴 [{hora}] VENTA   | {simbolo} | "
                          f"${precio} | RSI: {rsi} | "
                          f"Confirmaciones: {confirmaciones}/5")
                    if precio_compra:
                        diferencia = round(precio - precio_compra, 2)
                        porcentaje = round((diferencia / precio_compra) * 100, 2)
                        signo = "+" if diferencia >= 0 else ""
                        print(f"   💰 Simulación: compraste ${precio_compra} → "
                              f"vendiste ${precio} = {signo}{porcentaje}%")
                else:
                    print(f"⚪ [{hora}] NEUTRO  | {simbolo} | "
                          f"${precio} | RSI: {rsi} | "
                          f"Confirmaciones: {confirmaciones}/5")

                # Guardar en log
                guardar_en_log(simbolo, precio, rsi, senal,
                               confirmaciones, hora)

                # Enviar a Telegram solo si hay señal activa
                if senal == "COMPRA":
                    notificaciones.mensaje_compra(
                        simbolo, precio, rsi,
                        confirmaciones, soporte, resistencia
                    )
                    # Pedir análisis a la IA y mandarlo por Telegram
                    analisis = analista.analizar_si_hay_senal(resultado)
                    if analisis:
                        notificaciones.mensaje_analisis_ia(simbolo, analisis)

                elif senal == "VENTA":
                    notificaciones.mensaje_venta(
                        simbolo, precio, precio_compra,
                        rsi, confirmaciones
                    )
                    # Análisis IA también en venta
                    analisis = analista.analizar_si_hay_senal(resultado)
                    if analisis:
                        notificaciones.mensaje_analisis_ia(simbolo, analisis)

            except Exception as e:
                print(f"[Alertas] Error procesando resultado: {e}")

        monitor.evento_alerta.clear()

def guardar_en_log(simbolo, precio, rsi, senal, confirmaciones, hora):
    """Guarda las señales en archivo de texto."""
    with monitor.lock:
        with open("señales.log", "a", encoding="utf-8") as f:
            f.write(f"{hora} | {simbolo} | ${precio} | "
                    f"RSI: {rsi} | {senal} | "
                    f"Confirmaciones: {confirmaciones}/5\n")

def iniciar_alertas():
    """Lanza el hilo de alertas."""
    hilo = threading.Thread(target=procesar_alertas, daemon=True)
    hilo.start()
    return hilo