"""
bot_autodetect.py - Bot con detección automática de clientes
Detecta el cliente por número de WhatsApp, código de acceso o texto del mensaje
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.loader import ConfigLoader, get_config
from app.router import MessageRouter
from app.config import config
from app.cliente_cache import cliente_cache
from database import db

# Configurar logging desde variables de entorno
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
log_file = Path(config.LOG_FILE)
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BotAutoDetect:
    """
    Bot que detecta automáticamente el cliente por:
    - Identificador (número WhatsApp)
    - Código de acceso
    """
    
    def __init__(self):
        self.loader = ConfigLoader()
        self.routers = {}  # Cache de routers por cliente
        self.cache_timestamp = {}  # Timestamp de cada cache
        self.CACHE_TTL = 60  # 1 minuto de expiración
    
    def _get_cached_router(self, cliente_id: str) -> Optional[MessageRouter]:
        """Obtiene router del cache si no ha expirado."""
        if cliente_id in self.routers:
            timestamp = self.cache_timestamp.get(cliente_id, 0)
            if time.time() - timestamp < self.CACHE_TTL:
                return self.routers[cliente_id]
            else:
                # Cache expirado, limpiar
                logger.info(f"Cache expirado para cliente: {cliente_id}")
                del self.routers[cliente_id]
                del self.cache_timestamp[cliente_id]
        return None
    
    def _cache_router(self, cliente_id: str, router: MessageRouter):
        """Guarda router en cache con timestamp."""
        self.routers[cliente_id] = router
        self.cache_timestamp[cliente_id] = time.time()
        logger.info(f"Router cacheado para cliente: {cliente_id}")
    
    def detectar_cliente(self, identificador: str = None, codigo: str = None, 
                        canal: str = 'whatsapp') -> Optional[Dict]:
        """
        Detecta el cliente por identificador o código.
        
        Args:
            identificador: Número WhatsApp, token, etc.
            codigo: Código de acceso (PUB-001)
            canal: Canal de comunicación (whatsapp, telegram, web)
        
        Returns:
            Dict con info del cliente o None si no existe
        """
        # Buscar por identificador primero
        if identificador:
            cliente = db.obtener_cliente_por_identificador(identificador, canal)
            if cliente:
                return cliente
        
        # Buscar por código de acceso
        if codigo:
            cliente = db.obtener_cliente_por_codigo(codigo)
            if cliente:
                return cliente
        
        return None
    
    def get_router(self, cliente_id: str) -> Optional[MessageRouter]:
        """Obtiene o crea un router para el cliente (con cache)."""
        # Intentar obtener del cache
        router = self._get_cached_router(cliente_id)
        if router:
            return router
        
        # Crear nuevo router
        config = get_config(cliente_id)
        if config:
            router = MessageRouter(config)
            self._cache_router(cliente_id, router)
            return router
        
        return None
    
    def procesar_mensaje(self, mensaje: str, user_id: str, 
                         identificador: str = None, codigo: str = None,
                         canal: str = 'whatsapp') -> Dict:
        """
        Procesa un mensaje detectando automáticamente el cliente.
        Si no encuentra el cliente, usa 'publiya7' como cliente por defecto.
        """
        # Detectar cliente
        cliente = self.detectar_cliente(identificador, codigo, canal)
        
        # Si no se encuentra cliente, usar publiya7 como default
        if not cliente:
            logger.warning(f"Cliente no encontrado para identificador: {identificador}. Usando publiya7 por defecto.")
            cliente = {
                'cliente_id': 'publiya7',
                'nombre': 'Publiya7',
                'whatsapp': identificador or 'default'
            }
        
        cliente_id = cliente['cliente_id']
        logger.info(f"Cliente detectado: {cliente_id} para usuario: {user_id}")
        
        # Obtener router para este cliente
        router = self.get_router(cliente_id)
        
        if not router:
            logger.error(f"Error cargando router para cliente: {cliente_id}")
            return {
                'texto': "❌ Error cargando configuración del negocio. "
                        "Por favor intente más tarde.",
                'tipo': 'error',
                'error': True,
                'cliente_detectado': True
            }
        
        # Verificar si es usuario nuevo (no tiene estado previo)
        estado_previo = db.obtener_estado(cliente_id, user_id)
        es_nuevo_usuario = estado_previo is None or estado_previo.get('paso', 0) == 0
        
        # Procesar mensaje con el router del cliente
        try:
            # Si es saludo y usuario nuevo, mostrar bienvenida especial
            if es_nuevo_usuario and mensaje.lower().strip() in ['hola', 'buenas', 'hey', 'saludos']:
                config = get_config(cliente_id)
                nombre_negocio = config.get('nombre', 'nuestro negocio')
                eslogan = config.get('eslogan', '')
                
                # Generar menú principal (incluye saludo, eslogan y pregunta)
                respuesta_bienvenida = router.generar_menu_principal()
                
                # Guardar estado inicial
                db.guardar_estado(cliente_id, user_id, {
                    'paso': 0,
                    'categoria': None,
                    'producto': None,
                    'cantidad': None,
                    'total': 0
                })
                
                return {
                    'texto': respuesta_bienvenida,
                    'tipo': 'bienvenida',
                    'error': False,
                    'cliente_detectado': True,
                    'cliente_id': cliente_id,
                    'cliente_nombre': cliente.get('nombre'),
                    'es_nuevo_usuario': True
                }
            
            # Procesar mensaje normal
            respuesta, metadata = router.procesar_mensaje(
                mensaje, 
                user_id=user_id,
                cliente_id=cliente_id
            )
            
            return {
                'texto': respuesta,
                'tipo': metadata.get('tipo', 'general'),
                'metadata': metadata,
                'error': metadata.get('tipo') == 'error',
                'cliente_detectado': True,
                'cliente_id': cliente_id,
                'cliente_nombre': cliente.get('nombre'),
                'es_nuevo_usuario': es_nuevo_usuario
            }
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
            
            return {
                'texto': "Disculpe, ocurrió un error inesperado. "
                        "Nuestro equipo ha sido notificado.",
                'tipo': 'error',
                'error': True,
                'cliente_detectado': True
            }
    
    def get_info_sistema(self) -> Dict:
        """Obtiene información del sistema."""
        return {
            'clientes_registrados': len(self.routers),
            'modo': 'auto-detección',
            'canales_soportados': ['whatsapp', 'telegram', 'web']
        }


# Instancia global del bot
bot_autodetect = BotAutoDetect()


def procesar_mensaje_webhook(mensaje: str, user_id: str, 
                              identificador: str, canal: str = 'whatsapp') -> Dict:
    """
    Función helper para procesar mensajes desde webhook.
    Usada cuando llega un mensaje de WhatsApp/Telegram.
    """
    logger.info(f"Webhook recibido: usuario={user_id}, canal={canal}")
    return bot_autodetect.procesar_mensaje(
        mensaje=mensaje,
        user_id=user_id,
        identificador=identificador,
        canal=canal
    )


def procesar_mensaje_por_codigo(mensaje: str, user_id: str, 
                                 codigo: str) -> Dict:
    """
    Función helper para procesar mensajes por código de acceso.
    Usado para pruebas o autenticación manual.
    """
    logger.info(f"Autenticación por código: usuario={user_id}, codigo={codigo}")
    return bot_autodetect.procesar_mensaje(
        mensaje=mensaje,
        user_id=user_id,
        codigo=codigo
    )


def detectar_y_procesar_mensaje(mensaje: str, user_id: str, 
                                 canal: str = 'whatsapp') -> Dict:
    """
    Función principal para SaaS:
    1. Detecta si el usuario ya tiene cliente asignado
    2. Si no, detecta el cliente por el texto del mensaje
    3. Guarda la relación para futuros mensajes
    """
    logger.info(f"SaaS Webhook: usuario={user_id}, mensaje='{mensaje[:50]}...'")
    
    # 1. Verificar si el usuario ya tiene cliente asignado (BLOQUEO DE CAMBIO)
    cliente_id = cliente_cache.obtener_cliente_de_usuario(user_id)
    
    if cliente_id:
        logger.info(f"Usuario {user_id} ya tiene cliente asignado: {cliente_id}")
        
        # Verificar si está intentando cambiar de cliente (ignorar si es el caso)
        cliente_nuevo = cliente_cache.detectar_cliente_por_texto(mensaje)
        if cliente_nuevo and cliente_nuevo != cliente_id:
            logger.warning(f"Usuario {user_id} intentó cambiar de {cliente_id} a {cliente_nuevo} - BLOQUEADO")
            # Log del intento
            cliente_cache.log_deteccion(user_id, mensaje, cliente_nuevo, 'intento_cambio_bloqueado', False)
        
        # Usar el cliente asignado original
        return bot_autodetect.procesar_mensaje(
            mensaje=mensaje,
            user_id=user_id,
            identificador=cliente_id,
            canal=canal
        )
    
    # 2. Si no tiene cliente asignado, detectar por texto
    cliente_id_detectado = cliente_cache.detectar_cliente_por_texto(mensaje)
    
    if cliente_id_detectado:
        logger.info(f"🎯 Cliente detectado por texto: {cliente_id_detectado}")
        
        # Guardar relación para futuros mensajes
        cliente_cache.guardar_relacion_usuario_cliente(user_id, cliente_id_detectado, 'texto')
        
        # Log de detección exitosa
        cliente_cache.log_deteccion(user_id, mensaje, cliente_id_detectado, 'texto', True)
        
        # Obtener config del cliente para bienvenida personalizada
        config_cliente = cliente_cache.obtener_cliente(cliente_id_detectado)
        
        # Procesar mensaje
        respuesta = bot_autodetect.procesar_mensaje(
            mensaje=mensaje,
            user_id=user_id,
            identificador=cliente_id_detectado,
            canal=canal
        )
        
        # Agregar bienvenida personalizada si es el primer mensaje
        mensaje_bienvenida = config_cliente.get('mensaje_bienvenida', f"¡Hola! Bienvenido a {config_cliente.get('nombre', 'nuestro servicio')}")
        eslogan = config_cliente.get('eslogan', '')
        
        texto_bienvenida = f"👋 {mensaje_bienvenida}\n"
        if eslogan:
            texto_bienvenida += f"_{eslogan}_\n\n"
        else:
            texto_bienvenida += "\n"
        
        respuesta['texto'] = texto_bienvenida + respuesta['texto']
        
        return respuesta
    
    # 3. FALLBACK: Si no se detectó cliente, pedir nombre del negocio
    logger.warning(f"⚠️ No se detectó cliente para usuario {user_id}")
    
    # Log de detección fallida
    cliente_cache.log_deteccion(user_id, mensaje, None, 'fallback', False)
    
    return {
        'texto': "👋 ¡Hola! Bienvenido a BotlyPro.\n\n"
                 "Para atenderte mejor, por favor escribe el nombre de la empresa "
                 "con la que deseas comunicarte.\n\n"
                 "📌 *Ejemplos:*\n"
                 "• 'hola publiya7'\n"
                 "• 'imprenta xyz'\n"
                 "• O usa el enlace que te compartieron 🙌",
        'tipo': 'solicitud_cliente',
        'cliente_detectado': False
    }


# Prueba
if __name__ == "__main__":
    print("="*70)
    print("BOT CON AUTO-DETECCIÓN - PRUEBA")
    print("="*70)
    
    # Simular mensaje desde WhatsApp de Publiya7
    print("\n1. Simulando mensaje desde WhatsApp +573143909874 (Publiya7)...")
    
    respuesta = procesar_mensaje_webhook(
        mensaje="hola",
        user_id="cliente_final_123",
        identificador="+573143909874",
        canal="whatsapp"
    )
    
    print(f"\nCliente detectado: {respuesta.get('cliente_detectado')}")
    print(f"Cliente: {respuesta.get('cliente_nombre')}")
    print(f"Respuesta: {respuesta['texto'][:150]}...")
    
    # Simular mensaje con código
    print("\n2. Simulando autenticación por código PUB-001...")
    
    respuesta = procesar_mensaje_por_codigo(
        mensaje="hola",
        user_id="cliente_final_456",
        codigo="PUB-001"
    )
    
    print(f"\nCliente detectado: {respuesta.get('cliente_detectado')}")
    print(f"Cliente: {respuesta.get('cliente_nombre')}")
    print(f"Respuesta: {respuesta['texto'][:150]}...")
    
    # Simular número no registrado
    print("\n3. Simulando número no registrado...")
    
    respuesta = procesar_mensaje_webhook(
        mensaje="hola",
        user_id="cliente_final_789",
        identificador="+579999999999",
        canal="whatsapp"
    )
    
    print(f"\nCliente detectado: {respuesta.get('cliente_detectado')}")
    print(f"Error: {respuesta.get('error')}")
    print(f"Respuesta: {respuesta['texto']}")
    
    print("\n" + "="*70)
    print("PRUEBA COMPLETADA")
    print("="*70)
