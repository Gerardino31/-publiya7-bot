"""
registrar_clientes.py - Script para registrar clientes en la BD
"""

import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db

print("="*70)
print("REGISTRO DE CLIENTES EN EL SISTEMA")
print("="*70)

# Registrar Publiya7
print("\n1. Registrando Publiya7...")
resultado = db.registrar_cliente(
    cliente_id='publiya7',
    nombre='Publiya7 - Publicidad al Instante',
    telefono='+57 314 390 9874',
    email='publiya7@gmail.com',
    ciudad='Medellin',
    codigo_acceso='PUB-001',
    identificador='+573143909874',  # Numero WhatsApp sin espacios
    canal='whatsapp'
)

if resultado:
    print("   [OK] Publiya7 registrado")
    print("   Codigo de acceso: PUB-001")
    print("   Identificador: +573143909874")
else:
    print("   [ERROR] No se pudo registrar Publiya7")

# Registrar Imprenta XYZ (ejemplo)
print("\n2. Registrando Imprenta XYZ...")
resultado = db.registrar_cliente(
    cliente_id='imprentaxyz',
    nombre='Imprenta XYZ',
    telefono='+57 300 123 4567',
    email='contacto@imprentaxyz.com',
    ciudad='Bogota',
    codigo_acceso='XYZ-001',
    identificador='+573001234567',  # Numero WhatsApp de ejemplo
    canal='whatsapp'
)

if resultado:
    print("   [OK] Imprenta XYZ registrada")
    print("   Codigo de acceso: XYZ-001")
    print("   Identificador: +573001234567")
else:
    print("   [ERROR] No se pudo registrar Imprenta XYZ")

# Verificar registros
print("\n3. Verificando registros...")

cliente = db.obtener_cliente_por_codigo('PUB-001')
if cliente:
    print(f"   [OK] Publiya7 encontrado por codigo: {cliente['nombre']}")

cliente = db.obtener_cliente_por_identificador('+573143909874')
if cliente:
    print(f"   [OK] Publiya7 encontrado por identificador: {cliente['nombre']}")

print("\n" + "="*70)
print("REGISTRO COMPLETADO")
print("="*70)
print("\nAhora el sistema puede:")
print("  - Detectar clientes automaticamente por numero WhatsApp")
print("  - Autenticar clientes por codigo de acceso")
print("  - Escalar a multiples clientes")
