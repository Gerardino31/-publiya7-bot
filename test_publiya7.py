# Script de prueba para Publiya7
# Ejecutar: python test_publiya7.py

import sys
import os

# Agregar backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from services.bot_engine import BotEngine

print("=" * 60)
print("🚀 PUBLIYA7 - BOT DE ATENCIÓN AL CLIENTE")
print("=" * 60)
print()

# Crear instancia del bot para Publiya7
bot = BotEngine("publiya7")

# Mostrar información del cliente
print(f"📍 {bot.config['nombre_empresa']}")
print(f"📝 {bot.config.get('slogan', '')}")
print(f"📞 WhatsApp: {bot.config['telefono']}")
print(f"📧 Email: {bot.config['email']}")
print(f"🏙️  Ciudad: {bot.config['ciudad']}")
print(f"🕐 Horario: {bot.config['horario_atencion']}")
print()
print("=" * 60)
print()

# Simular conversación
pruebas = [
    ("hola", "👋 Saludo de bienvenida"),
    ("tarjetas de presentación", "💼 Producto con precios"),
    ("1000 unidades", "📊 Cotización tarjetas"),
    ("si", "✅ Confirmación"),
    ("etiquetas", "🏷️  Producto con precios por cantidad"),
    ("5000 unidades", "📊 Cotización etiquetas"),
    ("camisetas", "👕 Producto personalizado"),
    ("contacto", "📞 Información de contacto")
]

for mensaje, descripcion in pruebas:
    print(f"📝 {descripcion}")
    print(f"   Cliente: {mensaje}")
    print()
    
    respuesta = bot.procesar_mensaje(mensaje)
    
    # Mostrar respuesta con formato
    lineas = respuesta.split('\n')
    for linea in lineas:
        if linea.strip():
            print(f"   Bot: {linea}")
    print()
    print("-" * 60)
    print()

print("=" * 60)
print("✅ Prueba completada exitosamente!")
print("=" * 60)
print()
print("Para probar con otros productos, edita la lista 'pruebas'")
print("en este archivo.")
