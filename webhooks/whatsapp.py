"""
Webhook de WhatsApp Business API
Recibe mensajes de clientes y los procesa con el bot
"""

from flask import Flask, request, jsonify
import sys
import os

# Agregar el backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.bot_engine import BotEngine

app = Flask(__name__)

# Diccionario para mantener instancias de bots por cliente
bots = {}

@app.route('/webhook/whatsapp', methods=['POST'])
def recibir_mensaje_whatsapp():
    """
    Endpoint para recibir mensajes de WhatsApp Business API.
    
    Espera un JSON con:
    {
        "cliente_id": "imprenta_perez",
        "telefono_cliente": "+573001234567",
        "mensaje": "hola, necesito un adhesivo"
    }
    """
    try:
        data = request.json
        
        # Validar datos requeridos
        if not all(k in data for k in ['cliente_id', 'telefono_cliente', 'mensaje']):
            return jsonify({
                'error': 'Faltan datos requeridos',
                'requerido': ['cliente_id', 'telefono_cliente', 'mensaje']
            }), 400
        
        cliente_id = data['cliente_id']
        telefono = data['telefono_cliente']
        mensaje = data['mensaje']
        
        # Obtener o crear instancia del bot para este cliente
        if cliente_id not in bots:
            bots[cliente_id] = BotEngine(cliente_id)
        
        bot = bots[cliente_id]
        
        # Procesar el mensaje
        respuesta = bot.procesar_mensaje(mensaje)
        
        # Aquí iría el código para enviar la respuesta de vuelta a WhatsApp
        # Por ahora solo la devolvemos en la respuesta HTTP
        
        return jsonify({
            'success': True,
            'cliente_id': cliente_id,
            'telefono': telefono,
            'mensaje_recibido': mensaje,
            'respuesta': respuesta
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/webhook/whatsapp', methods=['GET'])
def verificar_webhook():
    """
    Endpoint para verificación del webhook por Meta/WhatsApp.
    Meta envía un challenge que debemos devolver.
    """
    # Esto es necesario para la verificación inicial de Meta
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # Token de verificación (debería estar en variables de entorno)
    VERIFY_TOKEN = "tu_token_secreto_aqui"
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return 'Verificación fallida', 403


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servicio está funcionando."""
    return jsonify({
        'status': 'ok',
        'servicio': 'webhook-whatsapp',
        'version': '1.0.0'
    }), 200


if __name__ == '__main__':
    print("=" * 50)
    print("WEBHOOK WHATSAPP - SERVIDOR DE PRUEBA")
    print("=" * 50)
    print()
    print("Endpoints disponibles:")
    print("  POST /webhook/whatsapp  - Recibir mensajes")
    print("  GET  /webhook/whatsapp  - Verificación Meta")
    print("  GET  /health            - Health check")
    print()
    print("Ejemplo de uso:")
    print('  curl -X POST http://localhost:5000/webhook/whatsapp \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"cliente_id": "imprenta_perez", "telefono_cliente": "+573001234567", "mensaje": "hola"}\'')
    print()
    
    # Ejecutar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
