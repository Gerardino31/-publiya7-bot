"""
prueba_persistencia.py - Prueba de persistencia de estado
Simula una conversacion, reinicia el bot, y verifica que recuerde el estado
"""

import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import crear_bot
from database import db

print("="*70)
print("PRUEBA DE PERSISTENCIA DE ESTADO")
print("="*70)

# Crear bot
bot = crear_bot('publiya7')

if not bot.esta_listo():
    print("[ERROR] Bot no pudo inicializarse")
    sys.exit(1)

user_id = "usuario_test_123"
cliente_id = "publiya7"

# Paso 1: Iniciar conversacion
print("\n1. INICIANDO CONVERSACION")
print("-"*70)
print("Usuario: hola")
resp = bot.procesar_mensaje("hola", user_id)
print(f"Bot: {resp['texto'][:80]}...")

# Paso 2: Seleccionar categoria
print("\nUsuario: 1 (Tarjetas)")
resp = bot.procesar_mensaje("1", user_id)
print(f"Bot: {resp['texto'][:80]}...")

# Paso 3: Seleccionar producto
print("\nUsuario: 2 (Sencilla UV 2 caras)")
resp = bot.procesar_mensaje("2", user_id)
print(f"Bot: {resp['texto'][:80]}...")

# Verificar estado guardado
print("\n2. VERIFICANDO ESTADO GUARDADO EN BD")
print("-"*70)
estado = db.obtener_estado(cliente_id, user_id)
if estado:
    print(f"[OK] Estado encontrado en BD:")
    print(f"   Paso: {estado['paso']}")
    print(f"   Categoria: {estado['categoria']}")
    print(f"   Producto: {estado['producto']}")
    print(f"   Fecha actualizacion: {estado['fecha_actualizacion']}")
else:
    print("[ERROR] No se encontro estado en BD")
    sys.exit(1)

# Paso 4: Simular reinicio del bot
print("\n3. SIMULANDO REINICIO DEL BOT")
print("-"*70)
print("Creando nueva instancia de bot...")
bot2 = crear_bot('publiya7')

# Paso 5: Continuar conversacion sin empezar de cero
print("\n4. CONTINUANDO CONVERSACION (sin decir 'hola')")
print("-"*70)
print("Usuario: 5000 (cantidad)")
resp = bot2.procesar_mensaje("5000", user_id)
print(f"Bot: {resp['texto'][:150]}...")

if resp['tipo'] == 'cotizacion':
    print("[OK] El bot recordo el estado y genero cotizacion!")
else:
    print(f"[ERROR] Tipo inesperado: {resp['tipo']}")

# Verificar que el pedido se guardo
print("\n5. VERIFICANDO PEDIDO GUARDADO")
print("-"*70)
print("Usuario: si (confirmar)")
resp = bot2.procesar_mensaje("si", user_id)
print(f"Bot: {resp['texto'][:100]}...")

if resp['tipo'] == 'pedido_confirmado':
    orden = resp['metadata'].get('orden')
    print(f"[OK] Pedido confirmado: {orden}")
    
    # Verificar en BD
    pedido = db.get_pedido(orden)
    if pedido:
        print(f"[OK] Pedido guardado en BD:")
        print(f"   Producto: {pedido['producto']}")
        print(f"   Total: ${pedido['precio_total']:,}")
    else:
        print("[ERROR] Pedido no encontrado en BD")
else:
    print(f"[ERROR] Tipo inesperado: {resp['tipo']}")

# Verificar que el estado se limpio
print("\n6. VERIFICANDO LIMPIEZA DE ESTADO")
print("-"*70)
estado = db.obtener_estado(cliente_id, user_id)
if estado is None:
    print("[OK] Estado limpiado correctamente despues del pedido")
else:
    print(f"[ADVERTENCIA] Estado aun existe: paso={estado['paso']}")

print("\n" + "="*70)
print("PRUEBA DE PERSISTENCIA COMPLETADA")
print("="*70)
print("\nEl bot ahora:")
print("  - Guarda estado en BD despues de cada mensaje")
print("  - Recuerda donde quedo el usuario al reiniciar")
print("  - Guarda pedidos en BD automaticamente")
print("  - Limpia estado despues de completar/cancelar")
