"""
canales/whatsapp.py - Canal WhatsApp (Twilio)
Adaptador para mensajes de WhatsApp via Twilio
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import PlainTextResponse
import sys
from pathlib import Path

router_whatsapp = APIRouter(prefix="/webhook")

def obtener_cliente_por_numero(numero_twilio: str) -> str:
    """Obtiene el cliente_id basado en el número de Twilio"""
    # Por ahora, asumimos publiya7 como default
    # En producción, buscar en base de datos
    return "publiya7"

def normalizar_usuario(from_number: str) -> str:
    """Crea ID único de usuario para este canal"""
    return f"whatsapp:{from_number}"

@router_whatsapp.post("/twilio")
async def webhook_twilio(
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...)
):
    """
    Webhook para mensajes de WhatsApp via Twilio
    """
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from app.router import MessageRouter
        
        # Normalizar contexto
        cliente_id = obtener_cliente_por_numero(To)
        usuario_id = normalizar_usuario(From)
        
        # Procesar mensaje con el motor existente
        # Cargar configuración del cliente
        config = {"nombre": "Publiya7", "cliente_id": cliente_id}
        
        router = MessageRouter(config, cliente_id)
        respuesta, metadata = router.procesar_mensaje(Body, usuario_id, cliente_id)
        
        # Retornar respuesta en formato Twilio
        return PlainTextResponse(
            f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{respuesta}</Message></Response>",
            media_type="application/xml"
        )
        
    except Exception as e:
        print(f"[ERROR WhatsApp] {e}")
        return PlainTextResponse(
            "<?xml version='1.0' encoding='UTF-8'?><Response><Message>Lo siento, hubo un error. Intenta de nuevo.</Message></Response>",
            media_type="application/xml"
        )
