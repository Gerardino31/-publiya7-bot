"""
main.py - Punto de entrada del bot multi-cliente
Ejecutar: python main.py
"""

import os
import sys

# Asegurar que estamos en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import crear_bot


def modo_interactivo():
    """Ejecuta el bot en modo interactivo (terminal)."""
    print("="*70)
    print("BOT MULTI-CLIENTE PARA IMPRENTAS")
    print("="*70)
    print("\nClientes disponibles:")
    print("  1. publiya7 (Medellin)")
    print("  2. imprentaxyz (Bogota)")
    print("\nEscribe 'salir' para terminar\n")
    
    # Seleccionar cliente
    cliente_id = input("¿Qué cliente desea usar? (publiya7): ").strip()
    if not cliente_id:
        cliente_id = "publiya7"
    
    # Crear bot
    bot = crear_bot(cliente_id)
    
    if not bot.esta_listo():
        print(f"\n❌ Error: No se pudo cargar el cliente '{cliente_id}'")
        print("Verifique que exista el archivo clientes/configs/{cliente_id}.json")
        return
    
    info = bot.get_info_cliente()
    print(f"\n✅ Bot activo: {info['nombre']}")
    print(f"📍 {info['ciudad']} | 📞 {info['telefono']}")
    print("="*70)
    
    # Bucle de conversación
    user_id = "usuario_terminal"
    
    while True:
        try:
            mensaje = input("\nCliente: ").strip()
            
            if mensaje.lower() in ['salir', 'exit', 'quit']:
                print("\nHasta luego!")
                break
            
            if not mensaje:
                continue
            
            # Procesar mensaje
            respuesta = bot.procesar_mensaje(mensaje, user_id)
            
            # Mostrar respuesta
            print(f"\nBot: {respuesta['texto']}")
            
            # Si es pedido confirmado, mostrar metadata
            if respuesta['tipo'] == 'pedido_confirmado':
                orden = respuesta['metadata'].get('orden', 'N/A')
                print(f"\nPedido guardado: {orden}")
            
        except KeyboardInterrupt:
            print("\n\nHasta luego!")
            break
        except Exception as e:
            print(f"\nError: {e}")


def modo_prueba():
    """Ejecuta pruebas automáticas."""
    print("🧹 Modo prueba no implementado aún")


if __name__ == "__main__":
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--prueba":
        modo_prueba()
    else:
        modo_interactivo()
