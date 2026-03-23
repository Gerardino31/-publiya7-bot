"""
validador_webhook.py - Valida y sanitiza entradas del webhook de WhatsApp
"""

import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ValidadorWebhook:
    """Valida mensajes entrantes de WhatsApp."""
    
    # Tipos de mensajes soportados
    TIPOS_SOPORTADOS = ['text']
    
    @staticmethod
    def validar_mensaje(data: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Valida el payload del webhook de WhatsApp.
        
        Returns:
            Tuple de (es_valido, error, datos_extraidos)
        """
        try:
            # Validar estructura básica
            if not isinstance(data, dict):
                return False, "Payload no es un diccionario", None
            
            # Extraer entry
            entry = data.get('entry', [])
            if not entry or not isinstance(entry, list):
                return False, "No se encontró 'entry' en el payload", None
            
            # Extraer changes
            changes = entry[0].get('changes', [])
            if not changes or not isinstance(changes, list):
                return False, "No se encontró 'changes' en el payload", None
            
            # Extraer value
            value = changes[0].get('value', {})
            if not value:
                return False, "No se encontró 'value' en el payload", None
            
            # Validar que hay mensajes
            messages = value.get('messages', [])
            if not messages:
                # Puede ser un evento de estado (delivery, read) - ignorar silenciosamente
                return False, None, {'tipo_evento': 'status_update'}
            
            message = messages[0]
            
            # Extraer información del remitente
            from_number = message.get('from')
            if not from_number:
                return False, "No se encontró número de remitente", None
            
            # Validar tipo de mensaje
            msg_type = message.get('type')
            if msg_type not in ValidadorWebhook.TIPOS_SOPORTADOS:
                logger.info(f"Tipo de mensaje no soportado: {msg_type}")
                return False, f"Tipo de mensaje '{msg_type}' no soportado. Solo texto.", {
                    'from': from_number,
                    'tipo': msg_type
                }
            
            # Extraer texto
            text_data = message.get('text', {})
            body = text_data.get('body', '').strip()
            
            if not body:
                return False, "Mensaje vacío", None
            
            # Validar longitud
            if len(body) > 4000:  # Límite razonable de WhatsApp
                logger.warning(f"Mensaje muy largo de {from_number}: {len(body)} caracteres")
                body = body[:4000]  # Truncar
            
            # Datos extraídos válidos
            datos = {
                'from': from_number,
                'texto': body,
                'message_id': message.get('id'),
                'timestamp': message.get('timestamp'),
                'tipo': msg_type
            }
            
            return True, None, datos
            
        except Exception as e:
            logger.error(f"Error validando mensaje: {e}", exc_info=True)
            return False, f"Error interno de validación: {str(e)}", None
    
    @staticmethod
    def validar_verificacion(data: dict, token_esperado: str) -> bool:
        """
        Valida el token de verificación del webhook.
        Usado cuando Meta verifica el endpoint.
        """
        mode = data.get('hub.mode')
        token = data.get('hub.verify_token')
        
        if mode == 'subscribe' and token == token_esperado:
            logger.info("Verificación de webhook exitosa")
            return True
        
        logger.warning(f"Verificación fallida: mode={mode}, token={token}")
        return False


# Instancia global
validador = ValidadorWebhook()


# Funciones helper
def validar_mensaje_entrante(data: dict) -> Tuple[bool, Optional[str], Optional[dict]]:
    """Valida un mensaje entrante de WhatsApp."""
    return ValidadorWebhook.validar_mensaje(data)


def es_mensaje_valido(data: dict) -> bool:
    """Verifica rápidamente si es un mensaje válido."""
    es_valido, _, _ = ValidadorWebhook.validar_mensaje(data)
    return es_valido
