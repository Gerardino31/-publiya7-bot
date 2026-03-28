"""
main.py - Servidor FastAPI para recibir webhooks de Twilio WhatsApp
"""

import os
import sys
import logging
from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import JSONResponse, PlainTextResponse
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de Twilio (desde variables de entorno)
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

# Crear aplicación FastAPI
app = FastAPI(title="BotlyPro Bot", version="1.0.0")

# Importar y registrar panel de administración
try:
    from admin.admin_panel import router as admin_router
    app.include_router(admin_router)
    logger.info("✅ Panel de administración cargado")
except Exception as e:
    logger.error(f"❌ Error cargando panel de administración: {e}")

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el servicio está funcionando."""
    return {
        "status": "ok",
        "message": "BotlyPro Bot está funcionando",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy"}

@app.post("/webhook")
async def receive_webhook(
    From: str = Form(...),
    Body: str = Form(default=""),
    To: str = Form(...),
    MessageSid: str = Form(...),
    NumMedia: str = Form(default="0"),
    MediaUrl0: str = Form(default=None),
    MediaContentType0: str = Form(default=None)
):
    """
    Recibe mensajes de WhatsApp desde Twilio.
    """
    try:
        # Importar aquí para evitar errores durante el arranque
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.bot_autodetect import bot_autodetect
        from database.database_saas import db_saas
        
        # Extraer número del remitente (quitar 'whatsapp:')
        from_number = From.replace('whatsapp:', '')
        
        # ============================================
        # V2: DETECTAR IMAGEN (Comprobante de pago)
        # ============================================
        if NumMedia != "0" and MediaUrl0:
            logger.info(f"📸 Imagen recibida de {from_number}: {MediaUrl0}")
            
            # Buscar pedido reciente pendiente de pago
            # Por ahora guardamos la imagen y notificamos
            # TODO: Implementar descarga y guardado de imagen
            
            respuesta_texto = "✅ Comprobante recibido.\n\n⏳ Verificando pago...\n\nTe notificaremos cuando sea confirmado."
            
            # Twilio espera una respuesta en formato TwiML
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{respuesta_texto}</Message>
</Response>"""
            
            return PlainTextResponse(content=twiml_response, media_type="application/xml")
        
        # ============================================
        # MENSAJE DE TEXTO NORMAL
        # ============================================
        logger.info(f"Mensaje recibido de {From}: {Body}")
        
        # Procesar mensaje con el bot
        respuesta = bot_autodetect.procesar_mensaje(
            mensaje=Body,
            user_id=from_number,
            identificador='twilio',
            canal='whatsapp'
        )
        
        mensaje_respuesta = respuesta.get('texto', '')
        logger.info(f"Respuesta del bot: {mensaje_respuesta}")
        
        # Twilio espera una respuesta en formato TwiML
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{mensaje_respuesta}</Message>
</Response>"""
        
        return PlainTextResponse(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}", exc_info=True)
        
        # Respuesta de error en TwiML
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Lo siento, ocurrió un error. Por favor intenta de nuevo.</Message>
</Response>"""
        
        return PlainTextResponse(content=error_response, media_type="application/xml")

@app.get("/recordatorios")
async def ejecutar_recordatorios():
    """Endpoint para ejecutar recordatorios (llamado por cron-job.org)"""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.recordatorios import enviar_recordatorios
        
        enviar_recordatorios()
        return {"status": "ok", "message": "Recordatorios procesados"}
    except Exception as e:
        logger.error(f"Error en recordatorios: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/info")
async def get_info():
    """Obtiene información del sistema."""
    return {
        "bot_name": "BotlyPro Bot",
        "version": "1.0.0",
        "provider": "Twilio"
    }

# Inicializar al arrancar
@app.on_event("startup")
async def startup_event():
    """Evento de inicio del servidor."""
    logger.info("=" * 70)
    logger.info("BOTLYPRO BOT - SERVIDOR INICIADO")
    logger.info("=" * 70)
    logger.info(f"URL: https://publiya7-bot.onrender.com")
    logger.info(f"Webhook: https://publiya7-bot.onrender.com/webhook")
    logger.info("Proveedor: Twilio WhatsApp")
    logger.info("=" * 70)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
