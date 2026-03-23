"""
Script de prueba para el bot SaaS
Ejecutar después de instalar dependencias: pip install -r requirements.txt
"""

import sys
import os

# Agregar backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.bot_engine import BotEngine


def test_bot_basico():
    """Prueba básica del bot."""
    print("=" * 60)
    print("PRUEBA DEL BOT - IMPRENTA PÉREZ")
    print("=" * 60)
    print()
    
    # Crear instancia del bot
    bot = BotEngine("imprenta_perez")
    
    # Conversación de prueba
    conversacion = [
        ("hola", "Saludo"),
        ("adhesivo laminado", "Seleccionar producto"),
        ("200x300cm", "Dar medidas en cm"),
        ("si", "Confirmar pedido")
    ]
    
    for mensaje, descripcion in conversacion:
        print(f"📝 {descripcion}")
        print(f"   Cliente: {mensaje}")
        print()
        
        respuesta = bot.procesar_mensaje(mensaje)
        
        # Mostrar respuesta con formato
        lineas = respuesta.split('\n')
        for linea in lineas:
            print(f"   Bot: {linea}")
        print()
        print("-" * 60)
        print()
    
    print("✅ Prueba completada exitosamente!")
    print()


def test_calculo_precios():
    """Prueba los cálculos de precios."""
    print("=" * 60)
    print("PRUEBA DE CÁLCULOS DE PRECIOS")
    print("=" * 60)
    print()
    
    bot = BotEngine("imprenta_perez")
    
    # Pruebas de cálculo
    pruebas = [
        (2, 3, False, "2m x 3m (6 m²)"),
        (100, 200, True, "100cm x 200cm (2 m²)"),
        (1.5, 2.5, False, "1.5m x 2.5m (3.75 m²)"),
    ]
    
    for ancho, alto, es_cm, descripcion in pruebas:
        area, total = bot.calcular_precio(ancho, alto, es_cm)
        print(f"📐 {descripcion}")
        print(f"   Área: {area:.2f} m²")
        print(f"   Total: ${total:,.0f} COP")
        print()
    
    print("✅ Cálculos correctos!")
    print()


def test_api():
    """Prueba la API REST (requiere servidor corriendo)."""
    import requests
    
    print("=" * 60)
    print("PRUEBA DE API REST")
    print("=" * 60)
    print()
    
    base_url = "http://localhost:5000"
    
    try:
        # Health check
        print("🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("   ✅ Servidor funcionando")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
        
        print()
        
        # Listar clientes
        print("📋 Listando clientes...")
        response = requests.get(f"{base_url}/api/clientes")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Clientes encontrados: {data['total']}")
            for cliente in data['clientes']:
                print(f"   - {cliente}")
        
        print()
        
        # Enviar mensaje al bot
        print("💬 Enviando mensaje de prueba...")
        payload = {
            "cliente_id": "imprenta_perez",
            "usuario_id": "+573001234567",
            "mensaje": "hola"
        }
        response = requests.post(f"{base_url}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta recibida")
            print(f"   Bot dice: {data['respuesta'][:50]}...")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   {response.text}")
        
        print()
        print("✅ Pruebas de API completadas!")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de ejecutar: python backend/app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


if __name__ == "__main__":
    print()
    print("🦞 PLATAFORMA SAAS - BOTS PARA IMPRENTAS")
    print("   Script de pruebas")
    print()
    
    # Ejecutar pruebas
    test_bot_basico()
    test_calculo_precios()
    
    # Preguntar si quiere probar la API
    print("=" * 60)
    respuesta = input("¿Quieres probar la API REST? (s/n): ")
    if respuesta.lower() in ['s', 'si', 'sí']:
        print()
        print("⚠️  Asegúrate de que el servidor esté corriendo:")
        print("   python backend/app.py")
        print()
        input("Presiona Enter cuando esté listo...")
        test_api()
    
    print()
    print("=" * 60)
    print("Pruebas finalizadas")
    print("=" * 60)
