"""
notificaciones.py - Sistema de notificaciones para nuevos pedidos
Envía alertas al dueño del negocio vía WhatsApp y Email
"""

import os
from typing import Dict, List
from datetime import datetime

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

class NotificadorPedidos:
    """Envía notificaciones cuando hay pedidos nuevos"""
    
    def __init__(self):
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        # Inicializar cliente Twilio si hay credenciales
        if TwilioClient and self.twilio_sid and self.twilio_token:
            self.twilio = TwilioClient(self.twilio_sid, self.twilio_token)
        else:
            self.twilio = None
    
    def notificar_nuevo_pedido(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> bool:
        """
        Envía notificación de nuevo pedido al dueño del negocio
        
        Args:
            cliente_config: Configuración del cliente (negocio)
            pedido: Datos del pedido
            items: Items del pedido
        """
        exito = True
        
        # Notificar por WhatsApp
        if cliente_config.get('notificar_whatsapp', True):
            if not self._notificar_whatsapp(cliente_config, pedido, items):
                exito = False
        
        # Notificar por Email (si está configurado)
        if cliente_config.get('notificar_email', False):
            if not self._notificar_email(cliente_config, pedido, items):
                exito = False
        
        return exito
    
    def _notificar_whatsapp(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> bool:
        """Envía notificación por WhatsApp al dueño"""
        if not self.twilio:
            print("⚠️ Twilio no configurado, no se puede enviar WhatsApp")
            return False
        
        telefono = cliente_config.get('telefono_notificaciones') or cliente_config.get('whatsapp')
        if not telefono:
            print("⚠️ No hay teléfono configurado para notificaciones")
            return False
        
        # Formatear número (agregar +57 si es colombiano)
        if telefono.startswith('3') and len(telefono) == 10:
            telefono = f"+57{telefono}"
        elif not telefono.startswith('+'):
            telefono = f"+{telefono}"
        
        # Construir mensaje
        mensaje = self._construir_mensaje_whatsapp(cliente_config, pedido, items)
        
        try:
            message = self.twilio.messages.create(
                from_=self.twilio_whatsapp,
                body=mensaje,
                to=f"whatsapp:{telefono}"
            )
            print(f"✅ WhatsApp enviado: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Error enviando WhatsApp: {e}")
            return False
    
    def _construir_mensaje_whatsapp(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> str:
        """Construye el mensaje de WhatsApp"""
        nombre_negocio = cliente_config.get('nombre', 'Tu negocio')
        
        mensaje = f"🛒 *¡NUEVO PEDIDO!*\n\n"
        mensaje += f"📦 Orden: {pedido.get('numero_orden')}\n"
        mensaje += f"💰 Total: ${pedido.get('total', 0):,} COP\n"
        mensaje += f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        mensaje += "*Productos:*\n"
        for item in items:
            if item.get('medidas'):
                cantidad = item['medidas']
            else:
                cantidad = f"{item.get('cantidad', 0):,} unid"
            
            mensaje += f"• {item.get('nombre_producto')}: {cantidad}\n"
        
        mensaje += f"\n*Cliente:*\n"
        mensaje += f"📱 {pedido.get('usuario_id', 'N/A')}\n"
        if pedido.get('nombre_comprador'):
            mensaje += f"👤 {pedido.get('nombre_comprador')}\n"
        
        mensaje += f"\n_Ingresa al panel para ver detalles: https://botlypro.com/admin_"
        
        return mensaje
    
    def _notificar_email(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> bool:
        """Envía notificación por Email (placeholder - implementar con servicio de email)"""
        email = cliente_config.get('email_notificaciones')
        if not email:
            return False
        
        # TODO: Implementar con SendGrid, AWS SES, o similar
        print(f"📧 Email de notificación pendiente para: {email}")
        return True

# Instancia global
notificador = NotificadorPedidos()
