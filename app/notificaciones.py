"""
notificaciones.py - Sistema de notificaciones para nuevos pedidos
Notificaciones desactivadas en Render free tier (SMTP bloqueado)
"""

from typing import Dict, List


class NotificadorPedidos:
    """Envía notificaciones cuando hay pedidos nuevos"""
    
    def __init__(self):
        print("ℹ️ Notificador inicializado (emails desactivados en Render free tier)")
    
    def notificar_nuevo_pedido(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> bool:
        """
        Notificación de nuevo pedido
        
        NOTA: Emails desactivados en Render free tier (SMTP bloqueado)
        Los pedidos se guardan en la base de datos y se pueden ver en el panel admin.
        """
        print(f"✅ Pedido {pedido.get('numero_orden')} guardado correctamente")
        print(f"💰 Total: ${pedido.get('total', 0):,} COP")
        print("ℹ️ Ver pedido en: /admin/pedidos")
        return True


# Instancia global
notificador = NotificadorPedidos()
