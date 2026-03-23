# Script de prueba interactivo para Publiya7
# Ejecutar: python bot_interactivo.py

import sys
import os

# Agregar backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from services.bot_engine import BotEngine

print("=" * 60)
print("🚀 PUBLIYA7 - BOT INTERACTIVO")
print("=" * 60)
print()
print("Escribe tus mensajes y el bot responderá.")
print("Escribe 'salir' para terminar.")
print("-" * 60)
print()

# Crear instancia del bot
bot = BotEngine("publiya7")

# Bucle interactivo
while True:
    try:
        # Leer entrada del usuario
        mensaje = input("Cliente: ").strip()
        
        # Verificar si quiere salir
        if mensaje.lower() in ['salir', 'exit', 'adios', 'chao']:
            print("\nBot: ¡Gracias por contactarnos! Hasta pronto.")
            break
        
        # Procesar mensaje y mostrar respuesta
        respuesta = bot.procesar_mensaje(mensaje)
        
        # Mostrar respuesta línea por línea
        print("Bot:", end=" ")
        lineas = respuesta.split('\n')
        for i, linea in enumerate(lineas):
            if i == 0:
                print(linea)
            else:
                print("    " + linea)
        print()
        
    except KeyboardInterrupt:
        print("\n\nBot: ¡Hasta luego!")
        break
    except Exception as e:
        print(f"\nError: {e}")
        print()

print("-" * 60)
print("Sesión finalizada.")
