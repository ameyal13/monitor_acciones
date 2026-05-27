# monitor.py - Monitoreo concurrente de acciones

import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
import indicadores
import config

# --- Recursos compartidos ---
lock = threading.Lock()
evento_alerta = threading.Event()
cola_resultados = queue.Queue()

precios_actuales = {}      # estado actual de cada acción
precios_compra = {}        # guarda el precio cuando se detectó COMPRA

def monitorear_accion(simbolo):
    """
    Función que corre en cada hilo.
    Procesa una acción completa y mete el resultado en la cola.
    """
    try:
        resultado = indicadores.procesar_accion(simbolo)

        if resultado is None:
            print(f"[{simbolo}] No hay suficientes datos todavía.")
            return

        # Lock para escribir en recursos compartidos
        with lock:
            senal_anterior = precios_actuales.get(simbolo, {}).get("senal", "NEUTRO")
            precios_actuales[simbolo] = resultado

            # Guardar precio de compra cuando aparece señal COMPRA
            if resultado["senal"] == "COMPRA" and senal_anterior != "COMPRA":
                precios_compra[simbolo] = resultado["precio"]

            # Adjuntar precio de compra al resultado para calcular ganancia
            resultado["precio_compra"] = precios_compra.get(simbolo, None)

        # Solo meter en cola si la señal cambió para no repetir alertas
        with lock:
            if resultado["senal"] != senal_anterior:
                cola_resultados.put(resultado)

                if resultado["senal"] in ["COMPRA", "VENTA"]:
                    evento_alerta.set()

    except Exception as e:
        print(f"[{simbolo}] Error: {e}")

def iniciar_monitoreo():
    """
    Lanza el monitoreo de todas las acciones usando ThreadPoolExecutor.
    Se repite cada INTERVALO_SEGUNDOS.
    """
    print("Iniciando monitoreo concurrente...")
    print(f"Acciones: {config.ACCIONES}")
    print(f"Intervalo: {config.INTERVALO_SEGUNDOS} segundos\n")

    while True:
        with ThreadPoolExecutor(max_workers=len(config.ACCIONES)) as executor:
            executor.map(monitorear_accion, config.ACCIONES)

        time.sleep(config.INTERVALO_SEGUNDOS)