"""
validacion_webhook.py - Validación de mensajes de WhatsApp
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ValidadorWebhook:
    """Valida mensajes entrantes de WhatsApp."""
    
    @staticmethod
    def validar_mensaje(data: dict) -> tuple:
        """
        Valida el formato de un mensaje de WhatsApp.
        
        Returns:
            (es_valido, mensaje_procesado, error)
        """
        try:
            # Verificar estructura básica
            if 'entry' not in data or not data['entry']:
                return False, None, "Estructura inválida: falta 'entry'"
            
            entry = data['entry'][0]
            
            if 'changes' not in entry or not entry['changes']:
                return False, None, "Estructura inválida: falta 'changes'"
            
            change = entry['changes'][0]
            
            if 'value' not in change:
                return False, None, "Estructura inválida: falta 'value'"
            
            value = change['value']
            
            # Verificar si es un mensaje
            if 'messages' not in value or not value['messages']:
                # Puede ser un estado (enviado, entregado, leído)
                if 'statuses' in value:
                    logger.debug("Recibido status update, ignorando")
                    return False, None, "status_update"
                return False, None, "No es un mensaje"
            
            message = value['messages'][0]
            
            # Verificar tipo de mensaje
            msg_type = message.get('type', 'unknown')
            
            if msg_type == 'text':
                # Mensaje de texto
                if 'text' not in message or 'body' not in message['text']:
                    return False, None, "Mensaje de texto sin contenido"
                
                texto = message['text']['body']
                numero = message.get('from', 'unknown')
                
                mensaje_procesado = {
                    'tipo': 'texto',
                    'texto': texto,
                    'numero': numero,
                    'id_mensaje': message.get('id', ''),
                    'timestamp': message.get('timestamp', '')
                }
                
                return True, mensaje_procesado, None
            
            elif msg_type == 'image':
                logger.info(f"Recibida imagen de {message.get('from', 'unknown')}")
                return False, None, "tipo_no_soportado:imagen"
            
            elif msg_type == 'audio':
                logger.info(f"Recibido audio de {message.get('from', 'unknown')}")
                return False, None, "tipo_no_soportado:audio"
            
            elif msg_type == 'document':
                logger.info(f"Recibido documento de {message.get('from', 'unknown')}")
                return False, None, "tipo_no_soportado:documento"
            
            else:
                logger.info(f"Tipo de mensaje no soportado: {msg_type}")
                return False, None, f"tipo_no_soportado:{msg_type}"
        
        except Exception as e:
            logger.error(f"Error validando mensaje: {e}")
            return False, None, f"error_validacion:{str(e)}"
    
    @staticmethod
    def validar_verificacion(data: dict, token_esperado: str) -> bool:
        """
        Valida la verificación del webhook de WhatsApp.
        """
        mode = data.get('hub.mode')
        token = data.get('hub.verify_token')
        
        if mode == 'subscribe' and token == token_esperado:
            return True
        
        return False


# Función helper rápida
def validar_mensaje_whatsapp(data: dict) -> tuple:
    """Valida un mensaje de WhatsApp."""
    return ValidadorWebhook.validar_mensaje(data)


if __name__ == "__main__":
    # Pruebas
    print("="*70)
    print("VALIDACIÓN DE WEBHOOK")
    print("="*70)
    
    # Mensaje de texto válido
    mensaje_valido = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "type": "text",
                        "from": "573001234567",
                        "text": {"body": "hola"},
                        "id": "msg123",
                        "timestamp": "1234567890"
                    }]
                }
            }]
        }]
    }
    
    print("\n1. Probando mensaje de texto válido...")
    valido, procesado, error = validar_mensaje_whatsapp(mensaje_valido)
    print(f"   Válido: {valido}")
    print(f"   Texto: {procesado['texto'] if procesado else 'N/A'}")
    print(f"   Número: {procesado['numero'] if procesado else 'N/A'}")
    
    # Mensaje de imagen
    mensaje_imagen = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{"type": "image", "from": "573001234567"}]
                }
            }]
        }]
    }
    
    print("\n2. Probando mensaje de imagen...")
    valido, procesado, error = validar_mensaje_whatsapp(mensaje_imagen)
    print(f"   Válido: {valido}")
    print(f"   Error: {error}")
    
    print("\n" + "="*70)
    print("Validación completada")
    print("="*70)
