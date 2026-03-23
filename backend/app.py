"""
Plataforma SaaS de Bots para Imprentas
Aplicación principal Flask
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Agregar backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from services.bot_engine import BotEngine

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde cualquier origen

# Almacenamiento en memoria de bots activos
# En producción esto debería ser Redis o base de datos
bots_activos = {}


@app.route('/')
def index():
    """Página de inicio."""
    return jsonify({
        'servicio': 'Bot SaaS para Imprentas',
        'version': '1.0.0',
        'endpoints': {
            'chat': '/api/chat',
            'clientes': '/api/clientes',
            'health': '/api/health'
        }
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint principal para conversaciones con el bot.
    
    Request JSON:
    {
        "cliente_id": "imprenta_perez",
        "usuario_id": "+573001234567",
        "mensaje": "hola, necesito un adhesivo"
    }
    
    Response JSON:
    {
        "success": true,
        "respuesta": "¡Hola! Bienvenido...",
        "paso": 1
    }
    """
    try:
        data = request.get_json()
        
        # Validar datos
        if not data or 'cliente_id' not in data or 'mensaje' not in data:
            return jsonify({
                'success': False,
                'error': 'Faltan datos requeridos: cliente_id, mensaje'
            }), 400
        
        cliente_id = data['cliente_id']
        usuario_id = data.get('usuario_id', 'anonimo')
        mensaje = data['mensaje']
        
        # Crear clave única para esta conversación
        conversacion_key = f"{cliente_id}:{usuario_id}"
        
        # Obtener o crear bot para esta conversación
        if conversacion_key not in bots_activos:
            bots_activos[conversacion_key] = BotEngine(cliente_id)
        
        bot = bots_activos[conversacion_key]
        
        # Procesar mensaje
        respuesta = bot.procesar_mensaje(mensaje)
        
        return jsonify({
            'success': True,
            'cliente_id': cliente_id,
            'usuario_id': usuario_id,
            'mensaje': mensaje,
            'respuesta': respuesta,
            'paso': bot.paso
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'error': f'Cliente no encontrado: {str(e)}'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    """Lista todos los clientes configurados."""
    try:
        configs_dir = 'clientes/configs'
        clientes = []
        
        if os.path.exists(configs_dir):
            for archivo in os.listdir(configs_dir):
                if archivo.endswith('.json'):
                    cliente_id = archivo.replace('.json', '')
                    clientes.append(cliente_id)
        
        return jsonify({
            'success': True,
            'clientes': clientes,
            'total': len(clientes)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clientes/<cliente_id>', methods=['GET'])
def obtener_cliente(cliente_id):
    """Obtiene información de un cliente específico."""
    try:
        import json
        config_path = f'clientes/configs/{cliente_id}.json'
        
        if not os.path.exists(config_path):
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado'
            }), 404
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # No exponer datos sensibles
        info_publica = {
            'nombre_empresa': config.get('nombre_empresa'),
            'ciudad': config.get('ciudad'),
            'horario_atencion': config.get('horario_atencion'),
            'productos': list(config.get('productos', {}).values())
        }
        
        return jsonify({
            'success': True,
            'cliente_id': cliente_id,
            'info': info_publica
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica que el servicio está funcionando."""
    return jsonify({
        'status': 'ok',
        'servicio': 'bot-saas-imprentas',
        'version': '1.0.0',
        'bots_activos': len(bots_activos)
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("PLATAFORMA SAAS - BOTS PARA IMPRENTAS")
    print("=" * 60)
    print()
    print("Servidor iniciado en: http://localhost:5000")
    print()
    print("Endpoints disponibles:")
    print("  GET  /                  - Info del servicio")
    print("  POST /api/chat          - Conversar con el bot")
    print("  GET  /api/clientes      - Listar clientes")
    print("  GET  /api/health        - Health check")
    print()
    print("Presiona Ctrl+C para detener")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
