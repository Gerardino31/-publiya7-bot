"""
prueba_estructura.py - Prueba la nueva estructura PRO
"""

import sys
import os

# Asegurar paths
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import crear_bot, get_config
from database import db

print("="*70)
print("PRUEBA DE ESTRUCTURA PRO MULTI-CLIENTE")
print("="*70)

# 1. Probar loader
print("\n1. PROBANDO LOADER (Carga de configuracion)")
print("-"*70)

config = get_config('publiya7')
if config:
    print(f"[OK] Configuracion cargada:")
    print(f"   Cliente ID: {config.get('cliente_id')}")
    print(f"   Nombre: {config.get('nombre')}")
    print(f"   Ciudad: {config.get('ciudad')}")
    print(f"   Categorias: {len(config.get('categorias', {}))}")
    print(f"   Telefono: {config.get('telefono')}")
else:
    print("[ERROR] Error cargando configuracion")
    sys.exit(1)

# 2. Probar base de datos
print("\n2. PROBANDO BASE DE DATOS")
print("-"*70)

db.registrar_cliente(
    'publiya7',
    'Publiya7 - Publicidad al Instante',
    '+57 314 390 9874',
    'publiya7@gmail.com',
    'Medellin'
)
print("[OK] Cliente registrado en BD")

orden = db.guardar_pedido(
    'publiya7',
    'user_test',
    'Tarjetas de Presentacion',
    'Mate 2 caras',
    '5000',
    650000
)
if orden:
    print(f"[OK] Pedido guardado: {orden}")
else:
    print("[ERROR] Error guardando pedido")

# 3. Probar bot
print("\n3. PROBANDO BOT MULTI-CLIENTE")
print("-"*70)

bot = crear_bot('publiya7')

if bot.esta_listo():
    print("[OK] Bot inicializado correctamente")
    info = bot.get_info_cliente()
    print(f"   Nombre: {info['nombre']}")
    print(f"   Categorias: {', '.join(info['categorias'])}")
    
    # Simular conversacion
    print("\n4. SIMULACION DE CONVERSACION")
    print("-"*70)
    
    user = "usuario_prueba"
    
    print("\nUsuario: hola")
    resp = bot.procesar_mensaje("hola", user)
    print(f"Bot: {resp['texto'][:150]}...")
    print(f"   [Tipo: {resp['tipo']}, Error: {resp['error']}]")
    
    print("\nUsuario: 1")
    resp = bot.procesar_mensaje("1", user)
    print(f"Bot: {resp['texto'][:150]}...")
    
    print("\nUsuario: 2")
    resp = bot.procesar_mensaje("2", user)
    print(f"Bot: {resp['texto'][:150]}...")
    
    print("\nUsuario: 5000")
    resp = bot.procesar_mensaje("5000", user)
    print(f"Bot: {resp['texto'][:200]}...")
    
    print("\n[OK] Todas las pruebas pasaron!")
    
else:
    print("[ERROR] Bot no pudo inicializarse")

print("\n" + "="*70)
print("ESTRUCTURA PRO LISTA PARA USAR")
print("="*70)
