"""
webhook_server.py - Servidor FastAPI para recibir webhooks de WhatsApp
"""

import os
import sys
import logging
from pathlib import Path

# Agregar path del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Response, HTTPException, Query
from fastapi.responses import PlainTextResponse
import uvicorn

from app.bot_autodetect import procesar_mensaje_webhook
from app.validador_webhook import validador
from app.config import config

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Bot WhatsApp - Publiya7",
    description="Servidor webhook para bot de WhatsApp multi-cliente",
    version="1.0.0"
)


@app.get("/")
def root():
    """Endpoint raíz para verificar que el servidor está activo."""
    return {
        "status": "online",
        "servicio": "Bot WhatsApp Publiya7",
        "version": "1.0.0",
        "whatsapp_configurado": config.esta_configurado_whatsapp()
    }


@app.get("/webhook")
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Endpoint de verificación del webhook.
    Meta llama a este endpoint para verificar el servidor.
    """
    logger.info(f"Solicitud de verificación: mode={hub_mode}, token={hub_verify_token}")
    
    if validador.validar_verificacion(
        {'hub.mode': hub_mode, 'hub.verify_token': hub_verify_token},
        config.WHATSAPP_VERIFY_TOKEN
    ):
        logger.info("Webhook verificado exitosamente")
        return PlainTextResponse(content=hub_challenge)
    
    logger.warning("Verificación de webhook fallida")
    raise HTTPException(status_code=403, detail="Verificación fallida")


@app.post("/webhook")
async def recibir_mensaje(request: Request):
    """
    Endpoint principal para recibir mensajes de WhatsApp.
    """
    try:
        # Leer payload
        data = await request.json()
        logger.debug(f"Payload recibido: {data}")
        
        # Validar mensaje
        es_valido, error, datos = validador.validar_mensaje(data)
        
        if not es_valido:
            if error:
                logger.warning(f"Mensaje inválido: {error}")
                # Enviar respuesta de error al usuario si tenemos su número
                if datos and datos.get('from'):
                    # Aquí podrías enviar mensaje de error vía WhatsApp API
                    pass
            else:
                # Evento de estado (delivery, read) - ignorar silenciosamente
                logger.debug("Evento de estado ignorado")
            
            return Response(content="OK", status_code=200)
        
        # Extraer datos
        numero_usuario = datos['from']
        texto = datos['texto']
        
        logger.info(f"Mensaje válido recibido de {numero_usuario}: {texto[:50]}...")
        
        # Detectar cliente por número de WhatsApp del negocio
        # En producción, esto viene del webhook de Meta
        # Por ahora usamos el identificador configurado
        identificador_negocio = config.WHATSAPP_PHONE_NUMBER_ID
        
        # Procesar mensaje
        respuesta = procesar_mensaje_webhook(
            mensaje=texto,
            user_id=numero_usuario,
            identificador=identificador_negocio,
            canal="whatsapp"
        )
        
        if respuesta.get('error'):
            logger.error(f"Error procesando mensaje: {respuesta.get('texto')}")
        else:
            logger.info(f"Respuesta generada: {respuesta.get('tipo')}")
            
            # Aquí enviarías la respuesta de vuelta a WhatsApp
            # TODO: Implementar envío vía WhatsApp API
            logger.info(f"Respuesta para usuario: {respuesta['texto'][:100]}...")
        
        return Response(content="OK", status_code=200)
        
    except Exception as e:
        logger.error(f"Error en webhook: {e}", exc_info=True)
        # Siempre responder 200 a WhatsApp para evitar reintentos
        return Response(content="OK", status_code=200)


@app.get("/health")
def health_check():
    """Endpoint de health check para monitoreo."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "whatsapp_configurado": config.esta_configurado_whatsapp()
    }


if __name__ == "__main__":
    from datetime import datetime
    
    print("="*70)
    print("SERVIDOR WEBHOOK - BOT WHATSAPP")
    print("="*70)
    
    # Validar configuración
    errores = config.validar_configuracion()
    if errores:
        print("\n[ADVERTENCIA] Configuración incompleta:")
        for error in errores:
            print(f"  - {error}")
        print("\nEl servidor iniciará pero WhatsApp no funcionará.")
        print("Complete el archivo .env con los valores de Meta.")
    else:
        print("\n[OK] Configuración completa")
    
    print(f"\nIniciando servidor en http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print("Presione Ctrl+C para detener")
    print("="*70)
    
    # Iniciar servidor
    uvicorn.run(
        app,
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        log_level=config.LOG_LEVEL.lower()
    )
