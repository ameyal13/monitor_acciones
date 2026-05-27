# main.py - Punto de entrada del programa

import threading
import time
import monitor
import alertas
import analista
import config

def hilo_analista():
    """
    Hilo separado que escucha la cola y llama a la IA
    cuando hay señales de compra o venta.
    """
    print("[Analista] Hilo de IA iniciado.\n")
    while True:
        try:
            # Espera un resultado en la cola (bloqueante)
            resultado = monitor.cola_resultados.get(timeout=5)
            analista.analizar_si_hay_senal(resultado)
        except Exception:
            # timeout sin resultados, seguimos esperando
            pass

def mostrar_resumen():
    """
    Hilo que imprime el estado actual de todas las acciones
    cada cierto tiempo.
    """
    while True:
        time.sleep(config.INTERVALO_SEGUNDOS)
        print("\n" + "="*50)
        print("      RESUMEN ACTUAL DE ACCIONES")
        print("="*50)

        with monitor.lock:
            if not monitor.precios_actuales:
                print("  Esperando datos...")
            else:
                for simbolo, datos in monitor.precios_actuales.items():
                    emoji = "🟢" if datos["senal"] == "COMPRA" else \
                            "🔴" if datos["senal"] == "VENTA" else "⚪"
                    print(f"  {emoji} {simbolo:6} | "
                          f"${datos['precio']:8} | "
                          f"RSI: {datos['rsi']:5} | "
                          f"{datos['senal']}")
        print("="*50 + "\n")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("   MONITOR DE ACCIONES CON IA")
    print("   Acciones:", ", ".join(config.ACCIONES))
    print("="*50 + "\n")

    # Hilo 1: alertas (escucha eventos)
    alertas.iniciar_alertas()

    # Hilo 2: analista IA (escucha la cola)
    hilo_ia = threading.Thread(target=hilo_analista, daemon=True)
    hilo_ia.start()

    # Hilo 3: resumen periódico
    hilo_resumen = threading.Thread(target=mostrar_resumen, daemon=True)
    hilo_resumen.start()

    # Hilo principal: monitoreo concurrente de acciones
    try:
        monitor.iniciar_monitoreo()
    except KeyboardInterrupt:
        print("\n\nMonitoreo detenido por el usuario.")
        print("Revisa el archivo señales.log para ver el historial.")