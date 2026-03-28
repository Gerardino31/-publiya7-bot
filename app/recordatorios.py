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

def obtener_pedidos_pendientes():
    """Obtiene pedidos pendientes de más de 24 horas"""
    conn = db_saas._get_connection()
    cursor = conn.cursor()
    
    hace_24h = (datetime.now() - timedelta(hours=24)).isoformat()
    
    cursor.execute("""
        SELECT p.id, p.numero_orden, p.cliente_id, p.usuario_id, 
               p.total, p.creado_en, p.estado, c.nombre as cliente_nombre
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.cliente_id
        WHERE p.estado = 'pendiente' 
        AND p.creado_en < ?
        LIMIT 50
    """, (hace_24h,))
    
    pedidos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return pedidos

def horas_desde(fecha_str):
    """Calcula horas transcurridas desde una fecha"""
    fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
    return (datetime.now() - fecha).total_seconds() / 3600

def enviar_mensaje_recordatorio(pedido):
    """Envía mensaje de recordatorio al cliente - optimizado para conversión"""
    
    # Obtener items del pedido para personalizar mensaje
    conn = db_saas._get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre_producto, cantidad 
        FROM pedido_items 
        WHERE pedido_id = ? LIMIT 1
    """, (pedido['id'],))
    item = cursor.fetchone()
    conn.close()
    
    # Construir mensaje persuasivo
    producto = item['nombre_producto'] if item else "tu producto"
    cantidad = item['cantidad'] if item else "varias unidades"
    
    mensaje = (
        f"👋 Hola, notamos que dejaste un pedido pendiente 🛒\n\n"
        f"📦 Producto: {producto}\n"
        f"🔢 Cantidad: {cantidad}\n"
        f"💰 Total: ${pedido['total']:,} COP\n\n"
        f"¿Deseas finalizar tu pedido ahora?\n"
        f"Responde *SI* y lo activamos ✅"
    )
    
    # TODO: Integrar con Twilio para enviar WhatsApp real
    print(f"📧 Recordatorio enviado a {pedido['usuario_id']}:")
    print(f"   {mensaje}")
    
    return True

def marcar_recordatorio_enviado(pedido_id):
    """Marca el pedido como recordatorio enviado"""
    conn = db_saas._get_connection()
    cursor = conn.cursor()
    
    # Agregar columna si no existe
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN recordatorio_enviado INTEGER DEFAULT 0")
    except:
        pass  # Columna ya existe
    
    cursor.execute("""
        UPDATE pedidos SET recordatorio_enviado = 1 WHERE id = ?
    """, (pedido_id,))
    
    conn.commit()
    conn.close()

def ya_fue_recordado(pedido_id):
    """Verifica si ya se envió recordatorio"""
    conn = db_saas._get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT recordatorio_enviado FROM pedidos WHERE id = ?", (pedido_id,))
        row = cursor.fetchone()
        conn.close()
        return row and row['recordatorio_enviado'] == 1
    except:
        conn.close()
        return False

def enviar_recordatorios():
    """Función principal: envía recordatorios para pedidos pendientes"""
    print(f"🔄 Iniciando recordatorios - {datetime.now()}")
    
    pedidos = obtener_pedidos_pendientes()
    enviados = 0
    
    for pedido in pedidos:
        # Filtros
        if pedido["estado"] != "pendiente":
            continue
        
        if ya_fue_recordado(pedido["id"]):
            continue
        
        if horas_desde(pedido["creado_en"]) < 24:
            continue
        
        # Enviar recordatorio
        if enviar_mensaje_recordatorio(pedido):
            marcar_recordatorio_enviado(pedido["id"])
            enviados += 1
    
    print(f"✅ {enviados} recordatorios enviados de {len(pedidos)} pedidos")

if __name__ == "__main__":
    enviar_recordatorios()
