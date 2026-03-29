"""
canales/telegram.py - Canal Telegram
Adaptador para mensajes de Telegram Bot API
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import requests
import os
import sys
from pathlib import Path

router_telegram = APIRouter(prefix="/webhook")

# Token del bot de Telegram (desde variables de entorno)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

def obtener_cliente_por_bot(bot_username: str) -> tuple:
    """Obtiene el cliente_id y config basado en el bot de Telegram"""
    import json
    from pathlib import Path
    
    # Por ahora, default a publiya7
    cliente_id = "publiya7"
    
    # Cargar configuración completa del cliente
    config_path = Path(__file__).parent.parent / "clientes" / "configs" / f"{cliente_id}.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar config: {e}")
        config = {"nombre": "Publiya7", "cliente_id": cliente_id}
    
    return cliente_id, config

def normalizar_usuario(chat_id: str) -> str:
    """Crea ID único de usuario para este canal"""
    return f"telegram:{chat_id}"

def enviar_mensaje_telegram(chat_id: str, mensaje: str):
    """Envía respuesta a Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN no configurado")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "Markdown"
        }, timeout=10)
        print(f"[Telegram] Respuesta enviada: {response.status_code}")
    except Exception as e:
        print(f"[ERROR Telegram] {e}")

@router_telegram.post("/telegram")
async def webhook_telegram(request: Request):
    """
    Webhook para mensajes de Telegram
    """
    try:
        data = await request.json()
        
        # Extraer datos del mensaje
        if "message" not in data:
            return JSONResponse({"status": "ok"})
        
        mensaje_data = data["message"]
        chat_id = str(mensaje_data["chat"]["id"])
        
        # Obtener texto del mensaje
        if "text" in mensaje_data:
            texto = mensaje_data["text"]
        else:
            texto = "[mensaje no texto]"
        
        # Obtener info del bot
        bot_info = data.get("message", {}).get("from", {})
        bot_username = bot_info.get("username", "unknown")
        
        # Normalizar contexto
        cliente_id, config = obtener_cliente_por_bot(bot_username)
        usuario_id = normalizar_usuario(chat_id)
        
        print(f"[Telegram] Mensaje de {usuario_id}: {texto[:50]}")
        
        # Procesar mensaje con el motor existente
        sys.path.append(str(Path(__file__).parent.parent))
        from app.router import MessageRouter
        
        router = MessageRouter(config, cliente_id)
        respuesta, metadata = router.procesar_mensaje(texto, usuario_id, cliente_id)
        
        # Enviar respuesta a Telegram
        enviar_mensaje_telegram(chat_id, respuesta)
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        print(f"[ERROR Telegram Webhook] {e}")
        return JSONResponse({"status": "error", "message": str(e)})

@router_telegram.get("/telegram")
async def verificar_webhook_telegram():
    """
    Verificación simple del webhook de Telegram
    """
    return JSONResponse({
        "status": "ok",
        "message": "Webhook de Telegram activo",
        "bot_configured": bool(TELEGRAM_BOT_TOKEN)
    })
