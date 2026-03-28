"""
core/observador.py - Observador de OpenClaw (Fase 1)

Este módulo permite que OpenClaw observe las decisiones sin interferir.
"""

def observar_openclaw(contexto):
    """
    Observa el contexto y obtiene la decisión que tomaría OpenClaw.
    
    Args:
        contexto: dict con información del mensaje y usuario
        
    Returns:
        str: decisión sugerida por OpenClaw o None
    """
    try:
        from core.openclaw_engine import decision_openclaw
        
        decision_ia = decision_openclaw(contexto)
        
        return decision_ia
        
    except Exception as e:
        print(f"[OBSERVADOR ERROR] {e}")
        return None
