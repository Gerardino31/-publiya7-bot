"""
canales/__init__.py - Paquete de canales multicanal
"""

from .whatsapp import router_whatsapp
from .telegram import router_telegram

__all__ = ['router_whatsapp', 'router_telegram']
