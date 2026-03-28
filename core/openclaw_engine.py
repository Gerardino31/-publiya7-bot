"""
core/openclaw_engine.py - Motor de decisión de OpenClaw (Fase 1: Observador)

Este módulo simula decisiones de IA para comparar con el sistema de reglas.
En Fase 1 solo observa, no decide.
"""

def decision_openclaw(contexto):
    """
    Analiza el contexto y sugiere una decisión basada en palabras clave.
    
    Args:
        contexto: dict con información del mensaje y usuario
        
    Returns:
        str: acción sugerida o None
    """
    try:
        mensaje = contexto.get("mensaje", "").lower()
        
        # 🧠 Simulación de inteligencia (baseline)
        
        if any(p in mensaje for p in ["comprar", "quiero", "pedido", "ordenar"]):
            return "procesar_compra"
        
        if any(p in mensaje for p in ["precio", "cuesta", "cotizar", "cuanto"]):
            return "cotizar"
        
        if "finalizar" in mensaje or "terminar" in mensaje:
            return "finalizar"
        
        if any(p in mensaje for p in ["asesor", "humano", "ayuda", "persona"]):
            return "escalar_humano"
        
        if any(p in mensaje for p in ["recomienda", "sugerir", "que me recomiendas"]):
            return "recomendar"
        
        if any(p in mensaje for p in ["menu", "inicio", "empezar"]):
            return "mostrar_menu"
        
        if any(p in mensaje for p in ["gracias", "ok", "perfecto", "listo"]):
            return "agradecer"
        
        return None
        
    except Exception as e:
        print(f"[OPENCLAW ENGINE ERROR] {e}")
        return None
