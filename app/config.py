"""
config.py - Carga configuración desde variables de entorno
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Configuración del sistema cargada desde variables de entorno."""
    
    # WhatsApp Business API
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
    WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', '')
    WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
    
    # Base de datos
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/pedidos.db')
    
    # Servidor
    SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Cliente
    DEFAULT_CLIENTE_ID = os.getenv('DEFAULT_CLIENTE_ID', 'publiya7')
    
    @classmethod
    def validar_configuracion(cls) -> list:
        """Valida que las variables críticas estén configuradas."""
        errores = []
        
        if not cls.WHATSAPP_ACCESS_TOKEN:
            errores.append("WHATSAPP_ACCESS_TOKEN no está configurado")
        
        if not cls.WHATSAPP_PHONE_NUMBER_ID:
            errores.append("WHATSAPP_PHONE_NUMBER_ID no está configurado")
        
        if not cls.WHATSAPP_VERIFY_TOKEN:
            errores.append("WHATSAPP_VERIFY_TOKEN no está configurado")
        
        return errores
    
    @classmethod
    def esta_configurado_whatsapp(cls) -> bool:
        """Verifica si WhatsApp está configurado."""
        return all([
            cls.WHATSAPP_ACCESS_TOKEN,
            cls.WHATSAPP_PHONE_NUMBER_ID,
            cls.WHATSAPP_VERIFY_TOKEN
        ])


# Instancia global
config = Config()
