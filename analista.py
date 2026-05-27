# analista.py - Análisis con IA (NVIDIA NIM)

from openai import OpenAI
import config

cliente = OpenAI(
    base_url=config.NVIDIA_BASE_URL,
    api_key=config.NVIDIA_API_KEY
)

def analizar_senal(simbolo, precio, rsi, senal):
    """
    Manda los datos de una acción a la IA y recibe un análisis
    en lenguaje natural.
    """
    prompt = f"""
    Eres un analista financiero experto. Analiza la siguiente señal técnica
    y explica en 3-4 oraciones qué significa y qué debería considerar un
    inversor principiante. Sé directo y claro, sin tecnicismos innecesarios.

    Acción: {simbolo}
    Precio actual: ${precio}
    RSI actual: {rsi}
    Señal detectada: {senal}
    
    Contexto:
    - RSI por encima de 70 indica sobrecompra
    - RSI por debajo de 30 indica sobreventa
    - La señal se basa en cruce de medias móviles (9 y 21 periodos)
    
    Proporciona un análisis breve y práctico.
    """

    try:
        respuesta = cliente.chat.completions.create(
            model=config.NVIDIA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un analista financiero educativo. \
                                Das análisis claros y honestos, siempre \
                                recordando que ninguna señal es garantía."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.5
        )
        return respuesta.choices[0].message.content

    except Exception as e:
        return f"[IA no disponible] Error: {e}"

def analizar_si_hay_senal(resultado):
    """
    Solo llama a la IA si la señal es COMPRA o VENTA.
    Para NEUTRO no gastamos tokens.
    """
    if resultado["senal"] in ["COMPRA", "VENTA"]:
        print(f"\n🤖 Analizando {resultado['simbolo']} con IA...")
        analisis = analizar_senal(
            resultado["simbolo"],
            resultado["precio"],
            resultado["rsi"],
            resultado["senal"]
        )
        print(f" Análisis IA: {analisis}\n")
        return analisis
    return None