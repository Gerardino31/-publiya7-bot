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
        
        # Obtener texto o foto del mensaje
        if "text" in mensaje_data:
            texto = mensaje_data["text"]
            es_imagen = False
            imagen_file_id = None
        elif "photo" in mensaje_data:
            # Es una imagen - obtener la de mejor calidad (última)
            fotos = mensaje_data["photo"]
            mejor_foto = fotos[-1]  # Última = mejor calidad
            imagen_file_id = mejor_foto["file_id"]
            texto = "[COMPROBANTE_PAGO]"
            es_imagen = True
            print(f"[Telegram] Imagen recibida: {imagen_file_id}")
        else:
            texto = "[mensaje no soportado]"
            es_imagen = False
            imagen_file_id = None
        
        # Obtener info del bot
        bot_info = data.get("message", {}).get("from", {})
        bot_username = bot_info.get("username", "unknown")
        
        # Normalizar contexto
        cliente_id, config = obtener_cliente_por_bot(bot_username)
        usuario_id = normalizar_usuario(chat_id)
        
        print(f"[Telegram] Mensaje de {usuario_id}: {texto[:50]}")
        
        # Si es imagen, guardar en base de datos como comprobante
        comprobante_guardado = False
        if es_imagen and imagen_file_id:
            try:
                sys.path.append(str(Path(__file__).parent.parent))
                from database.database_saas import db_saas
                
                # Obtener pedido pendiente del usuario
                # Adaptar query según base de datos
                from database.database_saas import USE_POSTGRES
                ph = "%s" if USE_POSTGRES else "?"
                
                conn = db_saas._get_connection()
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT id FROM pedidos 
                    WHERE cliente_id = {ph} AND usuario_id = {ph} AND estado = 'confirmado'
                    ORDER BY creado_en DESC LIMIT 1
                ''', (cliente_id, usuario_id))
                pedido = cursor.fetchone()
                conn.close()
                
                if pedido:
                    # Guardar comprobante
                    pedido_id = pedido['id']
                    
                    # Obtener URL real de la imagen de Telegram
                    # Primero llamar a getFile para obtener la ruta
                    getfile_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={imagen_file_id}"
                    try:
                        file_response = requests.get(getfile_url, timeout=10)
                        file_data = file_response.json()
                        if file_data.get('ok'):
                            file_path = file_data['result']['file_path']
                            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
                        else:
                            # Fallback: guardar el file_id y construir URL en el proxy
                            file_url = f"telegram://{imagen_file_id}"
                    except Exception as e:
                        print(f"[ERROR] Obteniendo file_path de Telegram: {e}")
                        file_url = f"telegram://{imagen_file_id}"
                    
                    db_saas.guardar_comprobante_pago(
                        cliente_id=cliente_id,
                        user_id=usuario_id,
                        pedido_id=pedido_id,
                        imagen_data=file_url.encode(),
                        content_type='image/jpeg'
                    )
                    print(f"[Telegram] Comprobante guardado para pedido {pedido_id}")
                    comprobante_guardado = True
                    
                    # Responder directamente sin pasar por el router
                    respuesta = f"✅ ¡Comprobante recibido!\n\nTu pedido *{pedido_id}* está en revisión.\n\nTe notificaremos cuando sea aprobado."
                    enviar_mensaje_telegram(chat_id, respuesta)
                    return JSONResponse({"status": "ok"})
                else:
                    print(f"[Telegram] No hay pedido pendiente para guardar comprobante")
                    respuesta = "⚠️ No tienes pedidos pendientes de pago.\n\nHaz un pedido primero para poder enviar comprobante."
                    enviar_mensaje_telegram(chat_id, respuesta)
                    return JSONResponse({"status": "ok"})
                    
            except Exception as e:
                print(f"[ERROR] Guardando comprobante Telegram: {e}")
                respuesta = "❌ Error al procesar el comprobante. Intenta de nuevo."
                enviar_mensaje_telegram(chat_id, respuesta)
                return JSONResponse({"status": "ok"})
        
        # Procesar mensaje con el motor existente (solo si no es imagen)
        sys.path.append(str(Path(__file__).parent.parent))
        from app.router import MessageRouter
        
        router = MessageRouter(config, cliente_id)
        respuesta, metadata = router.procesar_mensaje(texto, usuario_id, cliente_id)
        
        # Guardar log para Analytics (Fase 1 Observador)
        try:
            from core.logger import guardar_evento
            from core.observador import observar_openclaw
            
            contexto_log = {
                "mensaje": texto,
                "user_id": usuario_id,
                "cliente_id": cliente_id,
                "paso": None,
                "categoria": None
            }
            decision_ia = observar_openclaw(contexto_log)
            
            guardar_evento({
                "usuario_id": usuario_id,
                "cliente_id": cliente_id,
                "mensaje": texto[:200],
                "decision_reglas": metadata.get('tipo', 'desconocido'),
                "decision_ia": decision_ia,
                "decision_final": metadata.get('tipo', 'desconocido'),
                "paso_bot": None,
                "categoria": None
            })
        except Exception as e:
            print(f"[LOG ERROR Telegram] {e}")
        
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
