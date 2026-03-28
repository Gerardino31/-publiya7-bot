"""
recordatorios.py - Sistema de recordatorios automáticos para pedidos pendientes
Ejecutar como cron job cada 6 horas
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from database.database_saas import db_saas

def enviar_recordatorios():
    """Busca pedidos pendientes y envía recordatorios"""
    
    try:
        conn = db_saas._get_connection()
        cursor = conn.cursor()
        
        # Buscar pedidos pendientes de más de 24 horas
        hace_24h = (datetime.now() - timedelta(hours=24)).isoformat()
        
        cursor.execute("""
            SELECT p.id, p.numero_orden, p.cliente_id, p.usuario_id, 
                   p.total, p.creado_en, c.nombre as cliente_nombre
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.cliente_id
            WHERE p.estado = 'pendiente' 
            AND p.creado_en < ?
            AND (p.recordatorio_enviado IS NULL OR p.recordatorio_enviado = 0)
            LIMIT 10
        """, (hace_24h,))
        
        pedidos = cursor.fetchall()
        
        for pedido in pedidos:
            # Enviar recordatorio (placeholder - implementar con Twilio)
            print(f"📧 Recordatorio: Pedido {pedido['numero_orden']} - {pedido['usuario_id']}")
            
            # Marcar como recordatorio enviado
            cursor.execute("""
                UPDATE pedidos SET recordatorio_enviado = 1 WHERE id = ?
            """, (pedido['id'],))
        
        conn.commit()
        conn.close()
        
        print(f"✅ {len(pedidos)} recordatorios procesados")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    enviar_recordatorios()
