"""
bot.py - Nucleo del bot multi-cliente
Integra loader, router y base de datos
"""

import os
import sys
from typing import Dict, Optional

# Agregar paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.loader import ConfigLoader, get_config
from app.router import MessageRouter


class BotMultiCliente:
    """
    Bot generico que funciona con cualquier cliente.
    Carga configuracion dinamica y procesa mensajes.
    """
    
    def __init__(self, cliente_id: str = None):
        """
        Inicializa el bot para un cliente especifico.
        
        Args:
            cliente_id: ID del cliente (ej: 'publiya7'). 
                       Si es None, usa variable de entorno CLIENTE_ID
        """
        self.cliente_id = cliente_id or os.getenv('CLIENTE_ID', 'publiya7')
        self.config = None
        self.router = None
        self._cargar_configuracion()
    
    def _cargar_configuracion(self):
        """Carga la configuracion del cliente."""
        self.config = get_config(self.cliente_id)
        
        if self.config:
            self.router = MessageRouter(self.config)
            print(f"[OK] Bot listo para: {self.config.get('nombre', self.cliente_id)}")
        else:
            print(f"[ERROR] No se pudo cargar configuracion para {self.cliente_id}")
    
    def esta_listo(self) -> bool:
        """Verifica si el bot esta correctamente configurado."""
        return self.config is not None and self.router is not None
    
    def procesar_mensaje(self, mensaje: str, user_id: str = "default") -> Dict:
        """
        Procesa un mensaje y retorna respuesta completa.
        Con manejo de errores robusto para produccion.
        
        Args:
            mensaje: Texto del mensaje del usuario
            user_id: Identificador unico del usuario (para mantener estado)
        
        Returns:
            Dict con:
                - 'texto': Respuesta del bot
                - 'tipo': Tipo de respuesta
                - 'metadata': Informacion adicional
                - 'error': True si hubo error
        """
        # Verificar que el bot este listo
        if not self.esta_listo():
            return {
                'texto': "Lo siento, el servicio no esta disponible en este momento. Por favor intente mas tarde.",
                'tipo': 'error',
                'error': True
            }
        
        # Validar entrada
        if not mensaje or not isinstance(mensaje, str):
            return {
                'texto': "No recibi su mensaje. ¿Podria escribirlo de nuevo?",
                'tipo': 'error',
                'error': True
            }
        
        try:
            respuesta, metadata = self.router.procesar_mensaje(
                mensaje, 
                user_id, 
                cliente_id=self.cliente_id
            )
            return {
                'texto': respuesta,
                'tipo': metadata.get('tipo', 'general'),
                'metadata': metadata,
                'error': metadata.get('tipo') == 'error'
            }
        except Exception as e:
            print(f"[ERROR CRITICO] Error procesando mensaje: {e}")
            import traceback
            traceback.print_exc()
            return {
                'texto': "Disculpe, ocurrio un error inesperado. Nuestro equipo ha sido notificado. Por favor intente de nuevo en unos momentos.",
                'tipo': 'error',
                'error': True
            }
    
    def get_info_cliente(self) -> Dict:
        """Retorna informacion del cliente configurado."""
        if not self.config:
            return {}
        
        return {
            'cliente_id': self.cliente_id,
            'nombre': self.config.get('nombre'),
            'ciudad': self.config.get('ciudad'),
            'telefono': self.config.get('telefono'),
            'email': self.config.get('email'),
            'categorias': list(self.config.get('categorias', {}).keys())
        }
    
    def cambiar_cliente(self, nuevo_cliente_id: str) -> bool:
        """Cambia la configuracion a otro cliente."""
        self.cliente_id = nuevo_cliente_id
        self._cargar_configuracion()
        return self.esta_listo()


# Funcion helper para uso rapido
def crear_bot(cliente_id: str = None) -> BotMultiCliente:
    """Crea una instancia del bot."""
    return BotMultiCliente(cliente_id)


# Prueba
if __name__ == "__main__":
    print("="*70)
    print("BOT MULTI-CLIENTE - PRUEBA")
    print("="*70)
    
    # Crear bot para Publiya7
    bot = crear_bot('publiya7')
    
    if bot.esta_listo():
        info = bot.get_info_cliente()
        print(f"\nCliente: {info['nombre']}")
        print(f"Ubicacion: {info['ciudad']}")
        print(f"Contacto: {info['telefono']}")
        print(f"Categorias: {', '.join(info['categorias'])}")
        
        # Simular conversacion
        print("\n" + "="*70)
        print("SIMULACION DE CONVERSACION")
        print("="*70)
        
        mensajes = ["hola", "1", "2", "5000"]
        user = "usuario_prueba"
        
        for msg in mensajes:
            print(f"\nUsuario: {msg}")
            resp = bot.procesar_mensaje(msg, user)
            print(f"Bot: {resp['texto'][:200]}...")
            print(f"   [Tipo: {resp['tipo']}, Error: {resp['error']}]")
    else:
        print("[ERROR] El bot no pudo inicializarse")
