"""
main.py - Servidor FastAPI para recibir webhooks de WhatsApp
"""

import os
import sys
import logging
import requests
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de WhatsApp API
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
WHATSAPP_ACCESS_TOKEN = 'EAAU4ZAgdX7hEBRISQi4MmI6uPgxOxo5L8xZBPtqUdg8TlKeucC5RzcUl4PJHXmMZC3kg56mIxXs93lXdi5QYs3sPYmZAfCNxaHZAL9r0D4XPKolXjgXSZAmJUOWfXC784Ldgk8xWqYjOA9WIC8PkmZAeN6Hu2kau5awwxwxjONCjMdPnXDr0GBiBEplAQxxAosTOel9HSTIzkwXUc8dGCJhiToCi77Jp7UVrJ0kE0ouRoSjPepeL3Kwpk2E8LZBdovTMFpbZAmoAyk3rZBgGx622vxdvEZD'
WHATSAPP_PHONE_NUMBER_ID = '1033575916505556'

def enviar_mensaje_whatsapp(numero_destino: str, mensaje: str) -> bool:
    """
    Envía un mensaje de WhatsApp usando la API de Meta.
    """
    try:
        # Limpiar número (quitar el + si existe)
        if numero_destino.startswith('+'):
            numero_destino = numero_destino[1:]
        
        url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero_destino,
            "type": "text",
            "text": {
                "body": mensaje
            }
        }
        
        logger.info(f"Enviando mensaje a {numero_destino}: {mensaje[:50]}...")
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            logger.info(f"Mensaje enviado exitosamente a {numero_destino}")
            return True
        else:
            logger.error(f"Error enviando mensaje: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error en enviar_mensaje_whatsapp: {e}", exc_info=True)
        return False

# Crear aplicación FastAPI
app = FastAPI(title="Publiya7 Bot", version="1.0.0")

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el servicio está funcionando."""
    return {
        "status": "ok",
        "message": "Publiya7 Bot está funcionando",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verificación del webhook de WhatsApp.
    Meta envía una solicitud GET para verificar el webhook.
    """
    try:
        # Obtener parámetros de la URL
        params = request.query_params
        mode = params.get('hub.mode')
        token = params.get('hub.verify_token')
        challenge = params.get('hub.challenge')
        
        logger.info(f"Verificación webhook: mode={mode}, token={token}")
        
        # Verificar token
        verify_token = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'publiya7_webhook_token_2024')
        if mode == 'subscribe' and token == verify_token:
            logger.info("Webhook verificado correctamente")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.warning("Verificación de webhook fallida")
            return Response(content="Verification failed", status_code=403)
            
    except Exception as e:
        logger.error(f"Error en verificación webhook: {e}")
        return Response(content="Error", status_code=500)

@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Recibe mensajes de WhatsApp.
    Meta envía los mensajes del usuario a este endpoint.
    """
    try:
        # Importar aquí para evitar errores durante el arranque
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.bot_autodetect import bot_autodetect
        
        # Obtener el cuerpo del mensaje
        body = await request.json()
        
        logger.info(f"Webhook recibido: {json.dumps(body, indent=2)}")
        
        # Extraer información del mensaje
        entry = body.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        
        # Verificar si es un mensaje
        if 'messages' not in value:
            logger.info("No es un mensaje, ignorando")
            return JSONResponse(content={"status": "ignored"})
        
        message = value['messages'][0]
        
        # Verificar tipo de mensaje
        if message.get('type') != 'text':
            logger.info(f"Tipo de mensaje no soportado: {message.get('type')}")
            return JSONResponse(content={"status": "ignored"})
        
        # Extraer datos
        from_number = message.get('from')  # Número del usuario
        text = message['text']['body']  # Texto del mensaje
        
        logger.info(f"Mensaje de {from_number}: {text}")
        
        # Detectar cliente por número de teléfono del negocio
        metadata = value.get('metadata', {})
        business_phone = metadata.get('display_phone_number', '')
        
        # Procesar mensaje con el bot
        respuesta = bot_autodetect.procesar_mensaje(
            mensaje=text,
            user_id=from_number,
            identificador=business_phone,
            canal='whatsapp'
        )
        
        logger.info(f"Respuesta del bot: {respuesta}")
        
        # Enviar respuesta de vuelta a WhatsApp
        mensaje_respuesta = respuesta.get('texto', '')
        if mensaje_respuesta:
            enviado = enviar_mensaje_whatsapp(from_number, mensaje_respuesta)
            if enviado:
                logger.info(f"Respuesta enviada a {from_number}")
            else:
                logger.error(f"No se pudo enviar respuesta a {from_number}")
        
        return JSONResponse(content={
            "status": "processed",
            "respuesta": mensaje_respuesta
        })
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

@app.get("/info")
async def get_info():
    """Obtiene información del sistema."""
    return {
        "bot_name": "Publiya7 Bot",
        "version": "1.0.0"
    }

# Inicializar al arrancar
@app.on_event("startup")
async def startup_event():
    """Evento de inicio del servidor."""
    logger.info("=" * 70)
    logger.info("PUBLIYA7 BOT - SERVIDOR INICIADO")
    logger.info("=" * 70)
    logger.info(f"URL: https://publiya7-bot.onrender.com")
    logger.info(f"Webhook: https://publiya7-bot.onrender.com/webhook")
    logger.info("=" * 70)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
