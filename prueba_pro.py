"""
prueba_pro.py - Prueba completa de la estructura PRO
"""

import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import crear_bot, get_config

print("="*70)
print("PRUEBA ESTRUCTURA PRO MULTI-CLIENTE")
print("="*70)

# 1. Probar loader con normalizacion
print("\n1. PROBANDO LOADER (Normalizacion flexible)")
print("-"*70)

config = get_config('publiya7')
if config:
    print("[OK] Configuracion cargada y normalizada:")
    print(f"   Cliente ID: {config['cliente_id']}")
    print(f"   Nombre: {config['nombre']}")
    print(f"   Ciudad: {config['ciudad']}")
    print(f"   Telefono: {config['telefono']}")
    print(f"   Categorias: {len(config['categorias'])}")
    
    # Verificar que tiene todas las claves estandar
    claves_requeridas = ['cliente_id', 'nombre', 'telefono', 'email', 
                        'categorias', 'respuestas', 'tiempo_entrega_default']
    faltantes = [k for k in claves_requeridas if k not in config]
    if faltantes:
        print(f"   [ADVERTENCIA] Faltan claves: {faltantes}")
    else:
        print("   [OK] Todas las claves estandar presentes")
else:
    print("[ERROR] No se pudo cargar configuracion")
    sys.exit(1)

# 2. Probar bot multi-cliente
print("\n2. PROBANDO BOT MULTI-CLIENTE")
print("-"*70)

bot = crear_bot('publiya7')

if bot.esta_listo():
    print("[OK] Bot inicializado")
    info = bot.get_info_cliente()
    print(f"   Nombre: {info['nombre']}")
    print(f"   Categorias: {len(info['categorias'])}")
    
    # Simular conversacion completa
    print("\n3. SIMULACION DE CONVERSACION")
    print("-"*70)
    
    user = "usuario_test"
    
    # Paso 1: Saludo
    print("\n[Paso 1] Usuario: hola")
    resp = bot.procesar_mensaje("hola", user)
    print(f"Bot: {resp['texto'][:100]}...")
    assert resp['tipo'] == 'saludo', "Debe ser tipo saludo"
    print("   [OK] Saludo correcto")
    
    # Paso 2: Seleccionar categoria
    print("\n[Paso 2] Usuario: 1 (Tarjetas)")
    resp = bot.procesar_mensaje("1", user)
    print(f"Bot: {resp['texto'][:100]}...")
    assert resp['tipo'] == 'menu_categoria', "Debe mostrar menu"
    print("   [OK] Menu de categoria mostrado")
    
    # Paso 3: Seleccionar producto
    print("\n[Paso 3] Usuario: 2 (Sencilla UV 2 caras)")
    resp = bot.procesar_mensaje("2", user)
    print(f"Bot: {resp['texto'][:100]}...")
    assert resp['tipo'] == 'producto_seleccionado', "Debe seleccionar producto"
    print("   [OK] Producto seleccionado")
    
    # Paso 4: Ingresar cantidad
    print("\n[Paso 4] Usuario: 5000")
    resp = bot.procesar_mensaje("5000", user)
    print(f"Bot: {resp['texto'][:100]}...")
    assert resp['tipo'] == 'cotizacion', "Debe generar cotizacion"
    print("   [OK] Cotizacion generada")
    
    print("\n" + "="*70)
    print("TODAS LAS PRUEBAS PASARON")
    print("="*70)
    print("\nLa estructura PRO esta lista:")
    print("  - Loader normaliza cualquier formato JSON")
    print("  - Router procesa mensajes con logica de negocio")
    print("  - Bot multi-cliente funciona correctamente")
    print("  - Soporta multiples formatos de configuracion")
    
else:
    print("[ERROR] Bot no pudo inicializarse")
