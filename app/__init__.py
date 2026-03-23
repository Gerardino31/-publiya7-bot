"""
app - Paquete principal del bot multi-cliente
"""

from .bot import BotMultiCliente, crear_bot
from .loader import ConfigLoader, get_config
from .router import MessageRouter

__all__ = [
    'BotMultiCliente',
    'crear_bot',
    'ConfigLoader',
    'get_config',
    'MessageRouter'
]
