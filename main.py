"""
main.py - Servidor FastAPI para recibir webhooks de WhatsApp
"""

import os
import sys
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar path para importar módulos del bot
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.bot_autodetect import bot_autodetect
from app.config import config

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
        if mode == 'subscribe' and token == config.WHATSAPP_VERIFY_TOKEN:
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
        # En WhatsApp Business API, el número del negocio viene en 'metadata'
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
        # Aquí deberíamos llamar a la API de WhatsApp para enviar el mensaje
        # Por ahora solo registramos la respuesta
        
        return JSONResponse(content={
            "status": "processed",
            "respuesta": respuesta.get('texto', '')
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
        "version": "1.0.0",
        "clientes_registrados": len(bot_autodetect.routers),
        "configurado_whatsapp": config.esta_configurado_whatsapp()
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
