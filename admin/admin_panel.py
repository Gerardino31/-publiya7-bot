"""
admin_panel.py - Panel de Administración BotlyPro (Versión Simple)
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from datetime import datetime
import json

router = APIRouter(prefix="/admin")

ADMIN_USER = "admin"
ADMIN_PASS = "botlypro2024"

@router.get("/")
async def login_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>BotlyPro Admin</title></head>
    <body style="font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #667eea;">
        <div style="background: white; padding: 40px; border-radius: 10px; text-align: center;">
            <h1>🤖 BotlyPro</h1>
            <form method="POST" action="/admin/login">
                <input type="text" name="username" placeholder="Usuario" style="display: block; margin: 10px 0; padding: 10px; width: 200px;"><br>
                <input type="password" name="password" placeholder="Contraseña" style="display: block; margin: 10px 0; padding: 10px; width: 200px;"><br>
                <button type="submit" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">Ingresar</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.post("/login")
@router.get("/login")
async def login(username: str = Form(""), password: str = Form("")):
    if username == ADMIN_USER and password == ADMIN_PASS:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    if username or password:
        return HTMLResponse(content="<h1>Credenciales incorrectas</h1><a href='/admin'>Volver</a>")
    return HTMLResponse(content="<h1>Error</h1><a href='/admin'>Volver</a>")

def obtener_estadisticas():
    """Obtiene estadísticas de la base de datos"""
    stats = {
        'total_pedidos': 0,
        'total_ventas': 0,
        'pedidos_hoy': 0,
        'ventas_hoy': 0
    }
    
    try:
        from database.database_saas import db_saas
        conn = db_saas._get_connection()
        cursor = conn.cursor()
        
        # Total pedidos y ventas
        cursor.execute("SELECT COUNT(*) as total, COALESCE(SUM(total), 0) as ventas FROM pedidos")
        row = cursor.fetchone()
        stats['total_pedidos'] = row['total'] or 0
        stats['total_ventas'] = row['ventas'] or 0
        
        # Pedidos y ventas de hoy
        from datetime import datetime
        hoy = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) as total, COALESCE(SUM(total), 0) as ventas 
            FROM pedidos 
            WHERE date(creado_en) = date('now')
        """)
        row = cursor.fetchone()
        stats['pedidos_hoy'] = row['total'] or 0
        stats['ventas_hoy'] = row['ventas'] or 0
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Error obteniendo estadísticas: {e}")
    
    return stats

@router.get("/dashboard")
async def dashboard():
    # Cargar clientes
    clientes_dir = Path("clientes/configs")
    clientes = []
    if clientes_dir.exists():
        for config_file in clientes_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get('cliente_id'):  # Solo mostrar si tiene cliente_id
                        clientes.append({
                            'id': config.get('cliente_id'),
                            'nombre': config.get('nombre', 'Sin nombre'),
                            'telefono': config.get('telefono', 'N/A'),
                            'estado': config.get('estado', 'activo')
                        })
            except:
                pass
    
    # Obtener estadísticas
    stats = obtener_estadisticas()
    
    # Generar filas de la tabla
    filas = ""
    for c in clientes:
        estado_color = '#48bb78' if c['estado'] == 'activo' else '#a0aec0'
        estado_texto = '🟢 Activo' if c['estado'] == 'activo' else '⚪ Inactivo'
        toggle_texto = 'Desactivar' if c['estado'] == 'activo' else 'Activar'
        toggle_color = '#ed8936' if c['estado'] == 'activo' else '#48bb78'
        
        filas += f"""<tr>
            <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">{c['id']}</td>
            <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">{c['nombre']}</td>
            <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">{c['telefono']}</td>
            <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">
                <span style="color: {estado_color}; font-weight: bold;">{estado_texto}</span>
            </td>
            <td style="padding: 15px; border-bottom: 1px solid #e2e8f0;">
                <a href="/admin/cliente/{c['id']}" style="background: #667eea; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">Ver</a>
                <a href="/admin/cliente/{c['id']}/toggle" style="background: {toggle_color}; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">{toggle_texto}</a>
                <a href="/admin/cliente/{c['id']}/eliminar" style="background: #f56565; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;" onclick="return confirm('¿Eliminar este cliente?')">Eliminar</a>
            </td>
        </tr>"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - BotlyPro</title>
        <style>
            .stats-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #667eea; margin: 10px 0; }}
            .stat-label {{ color: #718096; font-size: 14px; }}
            .stat-hoy {{ background: #48bb78; color: white; }}
            .stat-hoy .stat-number {{ color: white; }}
            .stat-hoy .stat-label {{ color: #e6fffa; }}
        </style>
    </head>
    <body style="font-family: Arial; margin: 0; background: #f7fafc;">
        <div style="background: #2d3748; color: white; padding: 20px;">
            <h2>🤖 BotlyPro</h2>
        </div>
        <div style="padding: 30px; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h1>Dashboard</h1>
                <div>
                    <a href="/admin/pedidos" style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-right: 10px;">📦 Ver Pedidos</a>
                    <a href="/admin/nuevo-cliente" style="background: #48bb78; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">➕ Nuevo Cliente</a>
                </div>
            </div>
            
            <!-- Estadísticas -->
            <div class="stats-container">
                <div class="stat-card stat-hoy">
                    <div class="stat-label">📦 Pedidos Hoy</div>
                    <div class="stat-number">{stats['pedidos_hoy']}</div>
                </div>
                <div class="stat-card stat-hoy">
                    <div class="stat-label">💰 Ventas Hoy</div>
                    <div class="stat-number">${stats['ventas_hoy']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">📦 Total Pedidos</div>
                    <div class="stat-number">{stats['total_pedidos']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">💰 Total Ventas</div>
                    <div class="stat-number">${stats['total_ventas']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">👥 Clientes</div>
                    <div class="stat-number">{len(clientes)}</div>
                </div>
            </div>
            
            <!-- Tabla de clientes -->
            <h2 style="margin-top: 40px; color: #2d3748;">Clientes</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden;">
                <tr style="background: #667eea; color: white;">
                    <th style="padding: 15px; text-align: left;">ID</th>
                    <th style="padding: 15px; text-align: left;">Nombre</th>
                    <th style="padding: 15px; text-align: left;">Teléfono</th>
                    <th style="padding: 15px; text-align: left;">Estado</th>
                    <th style="padding: 15px; text-align: left;">Acción</th>
                </tr>
                {filas}
            </table>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.get("/cliente/{cliente_id}")
async def ver_cliente(cliente_id: str):
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    
    if not config_path.exists():
        return HTMLResponse(content="<h1>Cliente no encontrado</h1><a href='/admin/dashboard'>Volver</a>")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    nombre = config.get('nombre', 'Sin nombre')
    telefono = config.get('telefono', '')
    email = config.get('email', '')
    eslogan = config.get('eslogan', '')
    
    # Mensajes del bot
    mensajes = config.get('mensajes', {})
    pregunta = mensajes.get('pregunta', '¿En que podemos ayudarte?')
    despedida = mensajes.get('despedida', '')
    
    # Frases de cortesía
    frases = config.get('frases_cortesia', {})
    frase_general = frases.get('general', '¡Gracias por contactarnos!')
    frase_despedida = frases.get('despedida', '¡Que tengas un excelente día!')
    
    # FAQ
    faq = config.get('faq', {})
    faq_horario = faq.get('horario', 'Lunes a Viernes 8am - 6pm')
    faq_ubicacion = faq.get('ubicacion', 'Consultar dirección')
    faq_error = faq.get('no_entendi', 'Lo siento, no entendí. ¿Podrías reformularlo?')
    
    # No mostrar categorías aquí - usar botón "Ver Productos"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Cliente {cliente_id} - BotlyPro</title></head>
    <body style="font-family: Arial; margin: 0;">
        <div style="background: #2d3748; color: white; padding: 20px;">
            <h2>🤖 BotlyPro</h2>
        </div>
        <div style="padding: 30px;">
            <h1>Cliente: {nombre}</h1>
            <form method="POST" action="/admin/cliente/{cliente_id}/guardar">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Nombre:</label>
                    <input type="text" name="nombre" value="{nombre}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Teléfono:</label>
                    <input type="text" name="telefono" value="{telefono}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Email:</label>
                    <input type="email" name="email" value="{email}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Eslogan:</label>
                    <input type="text" name="eslogan" value="{eslogan}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Pregunta Final (menú principal):</label>
                    <input type="text" name="pregunta" value="{pregunta}" style="padding: 8px; width: 300px;">
                    <small style="color: #666;">Ej: ¿En qué podemos ayudarte?</small>
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Mensaje de Despedida:</label>
                    <input type="text" name="despedida" value="{despedida}" style="padding: 8px; width: 300px;">
                </div>
                <hr style="margin: 20px 0;">
                <h3 style="color: #48bb78;">📱 Enlace WhatsApp para tus Clientes</h3>
                <div style="background: #f0fff4; border: 2px solid #48bb78; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0 0 10px 0; font-weight: bold; color: #2d3748;">Comparte este enlace con tus clientes:</p>
                    <div style="background: white; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; font-size: 14px; margin-bottom: 15px;">
                        https://wa.me/14155238886?text=hola%20{cliente_id}
                    </div>
                    <button type="button" onclick="navigator.clipboard.writeText('https://wa.me/14155238886?text=hola%20{cliente_id}')" style="background: #48bb78; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">
                        📋 Copiar Enlace
                    </button>
                    <a href="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://wa.me/14155238886?text=hola%20{cliente_id}" target="_blank" style="background: #667eea; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        📱 Ver QR
                    </a>
                    <div style="margin-top: 15px; padding: 10px; background: #e6fffa; border-radius: 5px; font-size: 13px; color: #234e52;">
                        <strong>💡 Instrucciones para el dueño del negocio:</strong><br>
                        1. Copia este enlace<br>
                        2. Compártelo en tu página web, redes sociales o tarjetas<br>
                        3. Tus clientes harán click y serán atendidos automáticamente<br>
                        4. El bot responderá con tu nombre y productos
                    </div>
                </div>
                <hr style="margin: 20px 0;">
                <h3 style="color: #ed8936;">📧 Configuración de Notificaciones</h3>
                <div style="background: #fffaf0; border: 2px solid #ed8936; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0 0 15px 0; color: #744210;">Configura el email donde recibirás notificaciones de nuevos pedidos:</p>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: bold; color: #744210;">Email de Notificaciones:</label>
                        <input type="email" name="email_notificaciones" value="{config.get('email_notificaciones', email)}" style="padding: 8px; width: 300px; border: 1px solid #ed8936; border-radius: 4px;">
                        <small style="color: #744210; display: block; margin-top: 5px;">📩 Aquí llegarán los emails cuando haya pedidos nuevos</small>
                    </div>
                </div>
                
                <hr style="margin: 20px 0;">
                <h3 style="color: #38b2ac;">💳 Métodos de Pago</h3>
                <div style="background: #e6fffa; border: 2px solid #38b2ac; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0 0 15px 0; color: #234e52;">Configura cómo quieres que te paguen tus clientes:</p>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: bold; color: #234e52;">📱 Nequi / Daviplata:</label>
                        <input type="text" name="nequi_numero" value="{config.get('nequi_numero', telefono)}" style="padding: 8px; width: 300px; border: 1px solid #38b2ac; border-radius: 4px;">
                        <small style="color: #234e52; display: block; margin-top: 5px;">Número de celular para recibir pagos</small>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: bold; color: #234e52;">🏦 Banco:</label>
                        <input type="text" name="banco_nombre" value="{config.get('banco_nombre', '')}" style="padding: 8px; width: 300px; border: 1px solid #38b2ac; border-radius: 4px;" placeholder="Ej: Bancolombia, Davivienda">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: bold; color: #234e52;">💳 Tipo de Cuenta:</label>
                        <select name="banco_tipo_cuenta" style="padding: 8px; width: 300px; border: 1px solid #38b2ac; border-radius: 4px;">
                            <option value="" {'selected' if not config.get('banco_tipo_cuenta') else ''}>Seleccionar...</option>
                            <option value="ahorros" {'selected' if config.get('banco_tipo_cuenta') == 'ahorros' else ''}>Cuenta de Ahorros</option>
                            <option value="corriente" {'selected' if config.get('banco_tipo_cuenta') == 'corriente' else ''}>Cuenta Corriente</option>
                        </select>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; font-weight: bold; color: #234e52;">🔢 Número de Cuenta:</label>
                        <input type="text" name="banco_numero_cuenta" value="{config.get('banco_numero_cuenta', '')}" style="padding: 8px; width: 300px; border: 1px solid #38b2ac; border-radius: 4px;">
                    </div>
                    
                    <div>
                        <label style="display: block; font-weight: bold; color: #234e52;">💵 ¿Aceptas efectivo?</label>
                        <select name="acepta_efectivo" style="padding: 8px; width: 300px; border: 1px solid #38b2ac; border-radius: 4px;">
                            <option value="si" {'selected' if config.get('acepta_efectivo') == 'si' else ''}>Sí - Contra entrega</option>
                            <option value="no" {'selected' if config.get('acepta_efectivo') == 'no' else ''}>No - Solo transferencias</option>
                        </select>
                    </div>
                </div>
                
                <hr style="margin: 20px 0;">
                <h3 style="color: #667eea;">💬 Frases de Cortesía</h3>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Frase General:</label>
                    <input type="text" name="frase_general" value="{frase_general}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Frase de Despedida:</label>
                    <input type="text" name="frase_despedida" value="{frase_despedida}" style="padding: 8px; width: 300px;">
                </div>
                <hr style="margin: 20px 0;">
                <h3 style="color: #667eea;">❓ Respuestas Automáticas (FAQ)</h3>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Respuesta a "horario":</label>
                    <input type="text" name="faq_horario" value="{faq_horario}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Respuesta a "ubicación":</label>
                    <input type="text" name="faq_ubicacion" value="{faq_ubicacion}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Mensaje cuando no entiende:</label>
                    <input type="text" name="faq_error" value="{faq_error}" style="padding: 8px; width: 300px;">
                </div>
                <hr style="margin: 20px 0;">
                <button type="submit" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Guardar Cambios</button>
                <a href="/admin/dashboard" style="background: #718096; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Volver</a>
                <a href="/admin/cliente/{cliente_id}/productos" style="background: #48bb78; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">📦 Editar Productos y Precios</a>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.post("/cliente/{cliente_id}/guardar")
async def guardar_cliente(
    cliente_id: str, 
    nombre: str = Form(...), 
    telefono: str = Form(""), 
    email: str = Form(""), 
    eslogan: str = Form(""), 
    pregunta: str = Form(""), 
    despedida: str = Form(""), 
    frase_general: str = Form(""), 
    frase_despedida: str = Form(""), 
    faq_horario: str = Form(""), 
    faq_ubicacion: str = Form(""), 
    faq_error: str = Form(""),
    email_notificaciones: str = Form(""),
    nequi_numero: str = Form(""),
    banco_nombre: str = Form(""),
    banco_tipo_cuenta: str = Form(""),
    banco_numero_cuenta: str = Form(""),
    acepta_efectivo: str = Form("si")
):
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    
    if not config_path.exists():
        return HTMLResponse(content="<h1>Cliente no encontrado</h1>")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['nombre'] = nombre
    config['telefono'] = telefono
    config['email'] = email
    config['eslogan'] = eslogan
    
    # Guardar mensajes del bot
    if 'mensajes' not in config:
        config['mensajes'] = {}
    config['mensajes']['pregunta'] = pregunta
    config['mensajes']['despedida'] = despedida
    
    # Guardar frases de cortesía
    if 'frases_cortesia' not in config:
        config['frases_cortesia'] = {}
    config['frases_cortesia']['general'] = frase_general
    config['frases_cortesia']['despedida'] = frase_despedida
    
    # Guardar FAQ
    if 'faq' not in config:
        config['faq'] = {}
    config['faq']['horario'] = faq_horario
    config['faq']['ubicacion'] = faq_ubicacion
    config['faq']['no_entendi'] = faq_error
    
    # Guardar configuración de notificaciones
    print(f"[DEBUG] Guardando email_notificaciones: '{email_notificaciones}'")
    config['email_notificaciones'] = email_notificaciones if email_notificaciones else email
    print(f"[DEBUG] Email guardado en config: '{config.get('email_notificaciones')}'")
    
    # Guardar métodos de pago
    config['nequi_numero'] = nequi_numero if nequi_numero else telefono
    config['banco_nombre'] = banco_nombre
    config['banco_tipo_cuenta'] = banco_tipo_cuenta
    config['banco_numero_cuenta'] = banco_numero_cuenta
    config['acepta_efectivo'] = acepta_efectivo
    
    # Guardar archivo
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuración guardada: {cliente_id}")
    except Exception as e:
        print(f"❌ Error guardando: {e}")
        return HTMLResponse(content=f"<h1>Error al guardar</h1><p>{str(e)}</p>")
    
    return RedirectResponse(url=f"/admin/cliente/{cliente_id}", status_code=302)

@router.get("/cliente/{cliente_id}/productos")
async def ver_productos(cliente_id: str):
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    
    if not config_path.exists():
        return HTMLResponse(content="<h1>Cliente no encontrado</h1>")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    nombre = config.get('nombre', 'Sin nombre')
    categorias_dict = config.get('categorias', {})
    
    # Generar formulario de categorías y productos
    form_html = ""
    prod_idx = 0
    if isinstance(categorias_dict, dict):
        for cat_key, cat_data in categorias_dict.items():
            if isinstance(cat_data, dict):
                cat_nombre = cat_data.get('nombre', cat_key)
                # Campo editable para nombre de categoría
                form_html += f"""
                <div style="background: #e2e8f0; padding: 15px; margin-top: 20px; border-radius: 5px;">
                    <label style="font-weight: bold; color: #2d3748;">📦 Nombre Categoría:</label>
                    <input type="text" name="cat_nombre_{cat_key}" value="{cat_nombre}" style="padding: 8px; width: 300px; margin-left: 10px;">
                </div>
                """
                
                # Mostrar TODOS los productos editables
                tipos = cat_data.get('tipos', [])
                for tipo in tipos:
                    if isinstance(tipo, dict):
                        prod_id = tipo.get('id', f'prod_{prod_idx}')
                        prod_nombre = tipo.get('nombre', 'Sin nombre')
                        
                        # Detectar tipo de precio y campo
                        precio_field_name = ""
                        if 'precio_1000' in tipo:
                            precio_val = tipo.get('precio_1000', 0)
                            precio_field_name = f"prod_precio_{prod_idx}"
                            default_label = "Precio 1000 unid"
                        elif 'precio_cm2_con_terminado' in tipo:
                            precio_val = tipo.get('precio_cm2_con_terminado', 0)
                            precio_field_name = f"prod_precio_cm2_{prod_idx}"
                            default_label = "Precio cm2 c/terminado"
                        elif 'precio_cm2_sin_terminado' in tipo:
                            precio_val = tipo.get('precio_cm2_sin_terminado', 0)
                            precio_field_name = f"prod_precio_cm2_{prod_idx}"
                            default_label = "Precio cm2 s/terminado"
                        elif 'precio_cm2' in tipo:
                            precio_val = tipo.get('precio_cm2', 0)
                            precio_field_name = f"prod_precio_cm2_{prod_idx}"
                            default_label = "Precio por cm2"
                        else:
                            # Buscar cualquier campo de precio
                            precio_val = 0
                            precio_field_name = f"prod_precio_{prod_idx}"
                            default_label = "Precio"
                            for key in tipo.keys():
                                if 'precio' in key.lower():
                                    precio_val = tipo.get(key, 0)
                                    default_label = key.replace('_', ' ').title()
                                    break
                        
                        # Obtener label personalizado o usar default
                        precio_label_personalizado = tipo.get('precio_label', default_label)
                        
                        form_html += f"""
                        <div style="margin-bottom: 10px; padding: 10px; background: #f7fafc; border-radius: 5px; margin-left: 20px;">
                            <input type="hidden" name="prod_cat_{prod_idx}" value="{cat_key}">
                            <input type="hidden" name="prod_id_{prod_idx}" value="{prod_id}">
                            <label style="font-weight: bold;">Producto:</label>
                            <input type="text" name="prod_nombre_{prod_idx}" value="{prod_nombre}" style="padding: 5px; width: 250px; margin: 0 10px;">
                            <div style="margin-top: 8px;">
                                <label>Label del precio:</label>
                                <input type="text" name="prod_precio_label_{prod_idx}" value="{precio_label_personalizado}" style="padding: 5px; width: 200px; margin: 0 5px;">
                                <label>Precio: $</label>
                                <input type="number" name="{precio_field_name}" value="{precio_val}" step="0.1" style="padding: 5px; width: 100px;">
                            </div>
                        </div>
                        """
                        prod_idx += 1
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Productos - {nombre}</title></head>
    <body style="font-family: Arial; margin: 0;">
        <div style="background: #2d3748; color: white; padding: 20px;">
            <h2>🤖 BotlyPro</h2>
        </div>
        <div style="padding: 30px;">
            <h1>Editar Productos y Precios: {nombre}</h1>
            <a href="/admin/cliente/{cliente_id}" style="background: #718096; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Volver al Cliente</a>
            <hr style="margin: 20px 0;">
            <form method="POST" action="/admin/cliente/{cliente_id}/productos/guardar">
                {form_html}
                <button type="submit" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px;">Guardar Cambios</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.post("/cliente/{cliente_id}/productos/guardar")
@router.get("/cliente/{cliente_id}/productos/guardar")
async def guardar_productos(request: Request, cliente_id: str):
    try:
        config_path = Path(f"clientes/configs/{cliente_id}.json")
        
        if not config_path.exists():
            return HTMLResponse(content="<h1>Cliente no encontrado</h1>")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Obtener datos del formulario
        form_data = await request.form()
        
        # Actualizar nombres de categorías
        for key, value in form_data.items():
            if key.startswith('cat_nombre_'):
                cat_key = key.replace('cat_nombre_', '')
                if cat_key in config.get('categorias', {}):
                    if isinstance(config['categorias'][cat_key], dict):
                        config['categorias'][cat_key]['nombre'] = value
        
        # Actualizar productos (nombres y precios)
        prod_idx = 0
        while f'prod_id_{prod_idx}' in form_data:
            cat_key = form_data.get(f'prod_cat_{prod_idx}', '')
            prod_id = form_data.get(f'prod_id_{prod_idx}', '')
            prod_nombre = form_data.get(f'prod_nombre_{prod_idx}', '')
            
            if cat_key and prod_id and cat_key in config.get('categorias', {}):
                cat_data = config['categorias'][cat_key]
                if isinstance(cat_data, dict):
                    for tipo in cat_data.get('tipos', []):
                        if isinstance(tipo, dict) and tipo.get('id') == prod_id:
                            tipo['nombre'] = prod_nombre
                            
                            # Actualizar label del precio si existe
                            precio_label = form_data.get(f'prod_precio_label_{prod_idx}', '')
                            if precio_label:
                                tipo['precio_label'] = precio_label
                            
                            # Actualizar el precio según el campo que exista
                            if f'prod_precio_{prod_idx}' in form_data:
                                tipo['precio_1000'] = int(form_data.get(f'prod_precio_{prod_idx}', 0))
                            elif f'prod_precio_cm2_{prod_idx}' in form_data:
                                # Usar float para precios decimales (cm2)
                                precio_val = float(form_data.get(f'prod_precio_cm2_{prod_idx}', 0))
                                # Determinar qué campo de cm2 actualizar
                                if 'precio_cm2_con_terminado' in tipo:
                                    tipo['precio_cm2_con_terminado'] = precio_val
                                elif 'precio_cm2_sin_terminado' in tipo:
                                    tipo['precio_cm2_sin_terminado'] = precio_val
                                elif 'precio_cm2' in tipo:
                                    tipo['precio_cm2'] = precio_val
                                else:
                                    # Buscar cualquier campo de precio y actualizarlo
                                    for key in list(tipo.keys()):
                                        if 'precio' in key.lower():
                                            tipo[key] = precio_val
                                            break
                            break
            
            prod_idx += 1
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return RedirectResponse(url=f"/admin/cliente/{cliente_id}/productos", status_code=302)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error al guardar</h1><p>{str(e)}</p><a href='/admin/cliente/{cliente_id}/productos'>Volver</a>")

# ============================================
# NUEVO CLIENTE - ONBOARDING
# ============================================

@router.get("/nuevo-cliente")
async def nuevo_cliente_form():
    """Muestra formulario para crear nuevo cliente"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nuevo Cliente - BotlyPro</title>
        <style>
            body { font-family: Arial; margin: 0; background: #f7fafc; }
            .header { background: #2d3748; color: white; padding: 20px; }
            .container { max-width: 800px; margin: 30px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 20px; }
            label { display: block; font-weight: bold; margin-bottom: 5px; color: #4a5568; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 5px; font-size: 14px; }
            textarea { min-height: 80px; resize: vertical; }
            .btn { padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            .btn-primary { background: #667eea; color: white; }
            .btn-secondary { background: #e2e8f0; color: #4a5568; margin-left: 10px; }
            .section { border-left: 4px solid #667eea; padding-left: 20px; margin: 30px 0; }
            h2 { color: #2d3748; }
            .plantilla-info { background: #ebf8ff; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🤖 BotlyPro</h2>
        </div>
        <div class="container">
            <h1>➕ Nuevo Cliente</h1>
            <p style="color: #718096;">Completa la información para crear un nuevo negocio en BotlyPro.</p>
            
            <form method="POST" action="/admin/nuevo-cliente">
                
                <div class="section">
                    <h2>🏢 Datos del Negocio</h2>
                    
                    <div class="form-group">
                        <label>Nombre del Negocio *</label>
                        <input type="text" name="nombre" required placeholder="Ej: Publiya7">
                    </div>
                    
                    <div class="form-group">
                        <label>ID del Cliente *</label>
                        <input type="text" name="cliente_id" required placeholder="Ej: publiya7 (solo minúsculas, sin espacios)">
                    </div>
                    
                    <div class="form-group">
                        <label>Eslogan</label>
                        <input type="text" name="eslogan" placeholder="Ej: Publicidad al Instante">
                    </div>
                    
                    <div class="form-group">
                        <label>Teléfono WhatsApp *</label>
                        <input type="text" name="whatsapp" required placeholder="Ej: +57 314 390 9874">
                    </div>
                    
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email" placeholder="Ej: contacto@negocio.com">
                    </div>
                    
                    <div class="form-group">
                        <label>Ciudad</label>
                        <input type="text" name="ciudad" placeholder="Ej: Medellín">
                    </div>
                    
                    <div class="form-group">
                        <label>Dirección</label>
                        <textarea name="direccion" placeholder="Dirección del negocio"></textarea>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🤖 Configuración del Bot</h2>
                    
                    <div class="form-group">
                        <label>Plantilla Base</label>
                        <select name="plantilla">
                            <option value="imprenta">📇 Imprenta (Tarjetas, Volantes, Sellos...)</option>
                            <option value="restaurante">🍽️ Restaurante (Menú, Pedidos, Domicilios...)</option>
                            <option value="tienda">🛍️ Tienda (Productos, Inventario...)</option>
                            <option value="vacia">📝 Empezar en blanco</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Mensaje de Bienvenida</label>
                        <textarea name="mensaje_bienvenida" placeholder="¡Hola! Bienvenido a [nombre]..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Tono del Bot</label>
                        <select name="tono">
                            <option value="formal">Formal</option>
                            <option value="casual" selected>Casual / Amigable</option>
                            <option value="divertido">Divertido / Creativo</option>
                        </select>
                    </div>
                </div>
                
                <div class="section">
                    <h2>💎 Plan SaaS</h2>
                    
                    <div class="form-group">
                        <label>Plan</label>
                        <select name="plan">
                            <option value="basico">Básico - $49/mes (1,000 mensajes)</option>
                            <option value="pro" selected>Pro - $99/mes (5,000 mensajes)</option>
                            <option value="enterprise">Enterprise - $199/mes (Ilimitado)</option>
                        </select>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <button type="submit" class="btn btn-primary">✅ Crear Cliente</button>
                    <a href="/admin/dashboard" class="btn btn-secondary" style="text-decoration: none;">Cancelar</a>
                </div>
                
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.post("/nuevo-cliente")
async def crear_nuevo_cliente(
    nombre: str = Form(...),
    cliente_id: str = Form(...),
    eslogan: str = Form(""),
    whatsapp: str = Form(...),
    email: str = Form(""),
    ciudad: str = Form(""),
    direccion: str = Form(""),
    plantilla: str = Form("imprenta"),
    mensaje_bienvenida: str = Form(""),
    tono: str = Form("casual"),
    plan: str = Form("pro")
):
    """Crea el nuevo cliente con configuración inicial"""
    import os
    
    try:
        # Normalizar cliente_id
        cliente_id = cliente_id.lower().strip().replace(" ", "_")
        
        # Verificar que no exista
        config_path = Path(f"clientes/configs/{cliente_id}.json")
        if config_path.exists():
            return HTMLResponse(content=f"<h1>❌ Error</h1><p>El cliente '{cliente_id}' ya existe.</p><a href='/admin/nuevo-cliente'>Volver</a>")
        
        # Cargar plantilla base
        plantilla_config = cargar_plantilla(plantilla)
        
        # Crear configuración del cliente
        config = {
            "cliente_id": cliente_id,
            "nombre": nombre,
            "eslogan": eslogan or f"Bienvenido a {nombre}",
            "telefono": whatsapp,
            "whatsapp": whatsapp,
            "email": email,
            "ciudad": ciudad,
            "direccion": direccion,
            "plan": plan,
            "estado": "activo",
            "fecha_registro": datetime.now().isoformat(),
            "mensaje_bienvenida": mensaje_bienvenida or plantilla_config.get("mensaje_bienvenida", f"¡Hola! Bienvenido a {nombre}"),
            "tono": tono,
            "categorias": plantilla_config.get("categorias", {}),
            "frases_cortesia": plantilla_config.get("frases_cortesia", {}),
            "tiempo_entrega_default": "2-5 días hábiles"
        }
        
        # Guardar archivo JSON
        os.makedirs("clientes/configs", exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # Crear entrada en la base de datos
        try:
            from database.database_saas import db_saas
            conn = db_saas._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (cliente_id, nombre, eslogan, telefono, whatsapp, email, 
                                    ciudad, direccion, config_json, estado, plan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cliente_id, nombre, config["eslogan"], whatsapp, whatsapp, email,
                  ciudad, direccion, json.dumps(config), "activo", plan))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error guardando en BD: {e}")
        
        # Éxito
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Cliente Creado - BotlyPro</title></head>
        <body style="font-family: Arial; margin: 0; background: #f7fafc;">
            <div style="background: #2d3748; color: white; padding: 20px;">
                <h2>🤖 BotlyPro</h2>
            </div>
            <div style="max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #48bb78;">✅ ¡Cliente Creado!</h1>
                <p><strong>{nombre}</strong> ha sido registrado exitosamente.</p>
                <p>ID: <code>{cliente_id}</code></p>
                <p>Plan: {plan.upper()}</p>
                <br>
                <a href="/admin/dashboard" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Ir al Dashboard</a>
                <a href="/admin/cliente/{cliente_id}" style="background: #48bb78; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Configurar Productos</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>❌ Error al crear cliente</h1><p>{str(e)}</p><a href='/admin/nuevo-cliente'>Volver</a>")

def cargar_plantilla(tipo: str) -> dict:
    """Carga una plantilla base según el tipo de negocio"""
    
    plantillas = {
        "imprenta": {
            "mensaje_bienvenida": "¡Hola! 👋 Bienvenido a nuestro servicio de imprenta. ¿En qué podemos ayudarte hoy?",
            "categorias": {
                "tarjetas": {
                    "nombre": "🎴 Tarjetas de Presentación",
                    "tipo_cotizacion": "cantidad",
                    "unidad_base": 1000,
                    "tipos": [
                        {"id": "sencilla_uv", "nombre": "Sencilla Brillo UV", "precio_1000": 75000},
                        {"id": "mate", "nombre": "Mate Premium", "precio_1000": 119000}
                    ]
                },
                "volantes": {
                    "nombre": "📄 Volantes / Flyers",
                    "tipo_cotizacion": "cantidad",
                    "unidad_base": 1000,
                    "tipos": [
                        {"id": "volante_14", "nombre": "Cuarto de Carta", "precio_1000": 60000, "precio_2000": 114000, "precio_5000": 270000},
                        {"id": "volante_12", "nombre": "Media Carta", "precio_1000": 90000, "precio_2000": 171000, "precio_5000": 405000}
                    ]
                }
            },
            "frases_cortesia": {
                "bienvenida": ["¡Hola!", "¡Buen día!", "¡Bienvenido!"],
                "excelente_eleccion": ["¡Excelente elección!", "¡Perfecto!"],
                "cotizando": ["Estoy cotizando...", "Un momento por favor..."]
            }
        },
        "restaurante": {
            "mensaje_bienvenida": "¡Hola! 🍽️ Bienvenido a nuestro restaurante. ¿Qué te gustaría ordenar hoy?",
            "categorias": {
                "entradas": {
                    "nombre": "🥗 Entradas",
                    "tipo_cotizacion": "unitario",
                    "tipos": [
                        {"id": "ensalada", "nombre": "Ensalada César", "precio_unitario": 18000},
                        {"id": "sopa", "nombre": "Sopa del Día", "precio_unitario": 12000}
                    ]
                },
                "platos_fuertes": {
                    "nombre": "🍖 Platos Fuertes",
                    "tipo_cotizacion": "unitario",
                    "tipos": [
                        {"id": "pollo", "nombre": "Pechuga a la Plancha", "precio_unitario": 35000},
                        {"id": "carne", "nombre": "Filete de Res", "precio_unitario": 45000}
                    ]
                }
            },
            "frases_cortesia": {
                "bienvenida": ["¡Buen provecho!", "¡Hola!"],
                "excelente_eleccion": ["¡Excelente elección!", "¡Delicioso!"]
            }
        },
        "tienda": {
            "mensaje_bienvenida": "¡Hola! 🛍️ Bienvenido a nuestra tienda. ¿Qué estás buscando hoy?",
            "categorias": {
                "ropa": {
                    "nombre": "👕 Ropa",
                    "tipo_cotizacion": "unitario",
                    "tipos": [
                        {"id": "camiseta", "nombre": "Camiseta Básica", "precio_unitario": 45000},
                        {"id": "pantalon", "nombre": "Pantalón Jeans", "precio_unitario": 89000}
                    ]
                }
            },
            "frases_cortesia": {
                "bienvenida": ["¡Hola!", "¡Bienvenido!"],
                "excelente_eleccion": ["¡Gran elección!"]
            }
        },
        "vacia": {
            "mensaje_bienvenida": "¡Hola! Bienvenido. ¿En qué podemos ayudarte?",
            "categorias": {},
            "frases_cortesia": {
                "bienvenida": ["¡Hola!"],
                "excelente_eleccion": ["¡Perfecto!"]
            }
        }
    }
    
    return plantillas.get(tipo, plantillas["vacia"])

# ============================================
# GESTIÓN DE PEDIDOS
# ============================================

@router.get("/pedidos")
async def ver_pedidos():
    """Muestra lista de todos los pedidos"""
    
    # Obtener pedidos de la base de datos
    pedidos = []
    try:
        from database.database_saas import db_saas
        conn = db_saas._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, c.nombre as cliente_nombre 
            FROM pedidos p
            LEFT JOIN clientes c ON p.cliente_id = c.cliente_id
            ORDER BY p.creado_en DESC
        """)
        
        for row in cursor.fetchall():
            pedidos.append({
                'id': row['id'],
                'numero_orden': row['numero_orden'],
                'cliente_id': row['cliente_id'],
                'cliente_nombre': row['cliente_nombre'] or row['cliente_id'],
                'total': row['total'],
                'estado': row['estado'],
                'creado_en': row['creado_en']
            })
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Error cargando pedidos: {e}")
    
    # Generar filas de la tabla
    filas = ""
    for p in pedidos:
        estado_info = {
            'confirmado': {'color': '#48bb78', 'icono': '✅', 'bg': '#f0fff4'},
            'pendiente': {'color': '#ecc94b', 'icono': '⏳', 'bg': '#fffff0'},
            'procesando': {'color': '#4299e1', 'icono': '⚙️', 'bg': '#ebf8ff'},
            'completado': {'color': '#38a169', 'icono': '📦', 'bg': '#f0fff4'},
            'cancelado': {'color': '#f56565', 'icono': '❌', 'bg': '#fff5f5'}
        }.get(p['estado'], {'color': '#718096', 'icono': '❓', 'bg': '#f7fafc'})
        
        filas += f"""
        <tr style="background: {estado_info['bg']};">
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold;">{p['numero_orden']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{p['cliente_nombre']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #2d3748;">${p['total']:,} COP</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                <span style="background: {estado_info['color']}; color: white; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-flex; align-items: center; gap: 5px;">
                    {estado_info['icono']} {p['estado'].upper()}
                </span>
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #718096;">📅 {p['creado_en'][:10]}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                <a href="/admin/pedido/{p['id']}" style="background: #667eea; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: bold;">👁️ Ver</a>
            </td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pedidos - BotlyPro</title>
        <style>
            body {{ font-family: Arial; margin: 0; background: #f7fafc; }}
            .header {{ background: #2d3748; color: white; padding: 20px; }}
            .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
            .btn {{ padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .btn-primary {{ background: #667eea; color: white; }}
            .btn-success {{ background: #48bb78; color: white; }}
            table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden; margin-top: 20px; }}
            th {{ background: #667eea; color: white; padding: 15px; text-align: left; font-weight: 600; }}
            tr:hover {{ background: #f7fafc; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🤖 BotlyPro</h2>
        </div>
        <div class="container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h1>📦 Pedidos</h1>
                <a href="/admin/dashboard" class="btn btn-primary">← Volver al Dashboard</a>
            </div>
            
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <p style="margin: 0; color: #718096;">Total de pedidos: <strong style="color: #2d3748; font-size: 24px;">{len(pedidos)}</strong></p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Número</th>
                        <th>Cliente</th>
                        <th>Total</th>
                        <th>Estado</th>
                        <th>Fecha</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {filas if filas else '<tr><td colspan="6" style="padding: 40px; text-align: center; color: #718096;">No hay pedidos registrados</td></tr>'}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.get("/pedido/{pedido_id}")
async def ver_pedido_detalle(pedido_id: int):
    """Muestra el detalle completo de un pedido"""
    
    try:
        from database.database_saas import db_saas
        conn = db_saas._get_connection()
        cursor = conn.cursor()
        
        # Obtener información del pedido
        cursor.execute("""
            SELECT p.*, c.nombre as cliente_nombre, c.telefono as cliente_telefono, c.email as cliente_email
            FROM pedidos p
            LEFT JOIN clientes c ON p.cliente_id = c.cliente_id
            WHERE p.id = ?
        """, (pedido_id,))
        
        pedido = cursor.fetchone()
        if not pedido:
            conn.close()
            return HTMLResponse(content="<h1>Pedido no encontrado</h1><a href='/admin/pedidos'>Volver</a>")
        
        # Convertir sqlite3.Row a dict
        pedido = dict(pedido)
        
        # Obtener items del pedido
        cursor.execute("""
            SELECT * FROM pedido_items WHERE pedido_id = ?
        """, (pedido_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        # Convertir items a dict
        items = [dict(item) for item in items]
        
        # Generar filas de productos
        filas_items = ""
        for item in items:
            if item['medidas']:
                cantidad = item['medidas']
            else:
                cantidad = f"{item['cantidad']:,} unid"
            
            filas_items += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{item['nombre_producto']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{cantidad}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right;">${item['precio_unitario']:,}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">${item['subtotal']:,}</td>
            </tr>
            """
        
        # Color según estado
        estado_color = {
            'confirmado': '#48bb78',
            'pendiente': '#ecc94b',
            'procesando': '#4299e1',
            'completado': '#38a169',
            'cancelado': '#f56565'
        }.get(pedido['estado'], '#718096')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pedido #{pedido['numero_orden']} - BotlyPro</title>
            <style>
                body {{ font-family: Arial; margin: 0; background: #f7fafc; }}
                .header {{ background: #2d3748; color: white; padding: 20px; }}
                .container {{ padding: 30px; max-width: 1000px; margin: 0 auto; }}
                .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
                .btn {{ padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin-right: 10px; }}
                .btn-primary {{ background: #667eea; color: white; }}
                .btn-success {{ background: #48bb78; color: white; }}
                .btn-warning {{ background: #ed8936; color: white; }}
                .btn-danger {{ background: #f56565; color: white; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
                .estado-badge {{ background: {estado_color}; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; text-transform: uppercase; font-weight: bold; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .info-item {{ margin-bottom: 15px; }}
                .info-label {{ color: #718096; font-size: 12px; text-transform: uppercase; }}
                .info-value {{ font-size: 16px; font-weight: bold; color: #2d3748; }}
                .total {{ font-size: 24px; color: #48bb78; text-align: right; margin-top: 20px; padding-top: 20px; border-top: 2px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🤖 BotlyPro</h2>
            </div>
            <div class="container">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h1>📦 Pedido #{pedido['numero_orden']}</h1>
                    <div>
                        <a href="/admin/pedidos" class="btn btn-primary">← Volver a Pedidos</a>
                    </div>
                </div>
                
                <!-- Estado y Acciones -->
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="estado-badge">{pedido['estado']}</span>
                            <span style="margin-left: 15px; color: #718096;">{pedido['creado_en'][:19]}</span>
                        </div>
                        <div>
                            <form method="POST" action="/admin/pedido/{pedido_id}/estado" style="display: inline;">
                                <select name="nuevo_estado" style="padding: 8px; border-radius: 4px; border: 1px solid #ccc; margin-right: 10px;">
                                    <option value="pendiente" {'selected' if pedido['estado'] == 'pendiente' else ''}>Pendiente</option>
                                    <option value="confirmado" {'selected' if pedido['estado'] == 'confirmado' else ''}>Confirmado</option>
                                    <option value="procesando" {'selected' if pedido['estado'] == 'procesando' else ''}>Procesando</option>
                                    <option value="completado" {'selected' if pedido['estado'] == 'completado' else ''}>Completado</option>
                                    <option value="cancelado" {'selected' if pedido['estado'] == 'cancelado' else ''}>Cancelado</option>
                                </select>
                                <button type="submit" class="btn btn-warning">Actualizar Estado</button>
                            </form>
                        </div>
                    </div>
                </div>
                
                <!-- Información del Cliente -->
                <div class="card">
                    <h3 style="margin-top: 0; color: #667eea;">👤 Información del Cliente</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Teléfono</div>
                            <div class="info-value">{pedido['usuario_id']}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Nombre</div>
                            <div class="info-value">{pedido.get('nombre_comprador') or 'No especificado'}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Email</div>
                            <div class="info-value">{pedido.get('email_contacto') or 'No especificado'}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Dirección</div>
                            <div class="info-value">{pedido.get('direccion_entrega') or 'No especificada'}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Productos -->
                <div class="card">
                    <h3 style="margin-top: 0; color: #667eea;">📋 Productos</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th style="text-align: center;">Cantidad</th>
                                <th style="text-align: right;">Precio Unit.</th>
                                <th style="text-align: right;">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_items}
                        </tbody>
                    </table>
                    <div class="total">
                        TOTAL: ${pedido['total']:,} COP
                    </div>
                </div>
                
                <!-- Notas -->
                {f'<div class="card"><h3 style="margin-top: 0; color: #667eea;">📝 Notas</h3><p>{pedido.get("notas", "Sin notas")}</p></div>' if pedido.get('notas') else ''}
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
        
    except Exception as e:
        print(f"❌ Error mostrando pedido: {e}")
        return HTMLResponse(content=f"<h1>Error cargando pedido</h1><p>{str(e)}</p><a href='/admin/pedidos'>Volver</a>")

@router.post("/pedido/{pedido_id}/estado")
async def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str = Form(...)):
    """Actualiza el estado de un pedido"""
    try:
        from database.database_saas import db_saas
        conn = db_saas._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE pedidos SET estado = ? WHERE id = ?
        """, (nuevo_estado, pedido_id))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url=f"/admin/pedido/{pedido_id}", status_code=302)
    except Exception as e:
        print(f"❌ Error actualizando estado: {e}")
        return HTMLResponse(content=f"<h1>Error actualizando estado</h1><p>{str(e)}</p><a href='/admin/pedido/{pedido_id}'>Volver</a>")

@router.get("/cliente/{cliente_id}/eliminar")
async def eliminar_cliente(cliente_id: str):
    """Elimina un cliente del sistema"""
    try:
        # No permitir eliminar publiya7 (cliente principal)
        if cliente_id == 'publiya7':
            return HTMLResponse(content="<h1>❌ No se puede eliminar el cliente principal</h1><a href='/admin/dashboard'>Volver</a>")
        
        # Eliminar archivo JSON
        config_path = Path(f"clientes/configs/{cliente_id}.json")
        if config_path.exists():
            config_path.unlink()
        
        # Eliminar de la base de datos
        try:
            from database.database_saas import db_saas
            conn = db_saas._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE cliente_id = ?", (cliente_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error eliminando de BD: {e}")
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Cliente Eliminado - BotlyPro</title></head>
        <body style="font-family: Arial; margin: 0; background: #f7fafc;">
            <div style="background: #2d3748; color: white; padding: 20px;">
                <h2>🤖 BotlyPro</h2>
            </div>
            <div style="max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #48bb78;">✅ Cliente Eliminado</h1>
                <p>El cliente <strong>{cliente_id}</strong> ha sido eliminado.</p>
                <br>
                <a href="/admin/dashboard" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Volver al Dashboard</a>
            </div>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>❌ Error al eliminar</h1><p>{str(e)}</p><a href='/admin/dashboard'>Volver</a>")

# ============================================
# LOGIN Y DASHBOARD PARA CLIENTES
# ============================================

@router.get("/cliente-login")
async def cliente_login_page():
    """Página de login para clientes"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Acceso Clientes - BotlyPro</title>
        <style>
            body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .login-box { background: white; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-width: 400px; width: 90%; }
            h1 { color: #2d3748; margin-bottom: 10px; }
            .subtitle { color: #718096; margin-bottom: 30px; }
            input { display: block; margin: 15px 0; padding: 12px; width: 100%; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
            button { padding: 12px 30px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; }
            button:hover { background: #5a67d8; }
            .back-link { margin-top: 20px; color: #667eea; text-decoration: none; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🤖 BotlyPro</h1>
            <p class="subtitle">Acceso para Clientes</p>
            <form method="POST" action="/admin/cliente-login">
                <input type="text" name="cliente_id" placeholder="ID de tu negocio (ej: publiya7)" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Ingresar a mi Dashboard</button>
            </form>
            <a href="/admin/" class="back-link">← Volver al panel admin</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.post("/cliente-login")
async def cliente_login(cliente_id: str = Form(""), password: str = Form("")):
    """Autentica a un cliente"""
    # Verificar que el cliente existe
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    if not config_path.exists():
        return HTMLResponse(content="<h1>❌ Cliente no encontrado</h1><a href='/admin/cliente-login'>Volver</a>")
    
    # Cargar configuración del cliente
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Verificar contraseña (personalizada o por defecto)
    password_guardada = config.get('password', f"{cliente_id}2024")
    
    if password != password_guardada:
        return HTMLResponse(content="<h1>❌ Contraseña incorrecta</h1><a href='/admin/cliente-login'>Volver</a>")
    
    # Login exitoso - redirigir al dashboard del cliente
    return RedirectResponse(url=f"/admin/cliente-dashboard/{cliente_id}", status_code=302)

@router.get("/cliente-dashboard/{cliente_id}")
async def cliente_dashboard(cliente_id: str):
    """Dashboard de ventas para un cliente específico"""
    
    # Verificar que el cliente existe
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    if not config_path.exists():
        return HTMLResponse(content="<h1>❌ Cliente no encontrado</h1>")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    nombre_negocio = config.get('nombre', cliente_id)
    
    # Obtener estadísticas del cliente
    stats = obtener_estadisticas_cliente(cliente_id)
    
    # Generar HTML del dashboard
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - {nombre_negocio}</title>
        <style>
            body {{ font-family: Arial; margin: 0; background: #f7fafc; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }}
            .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
            .kpi-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
            .kpi-number {{ font-size: 36px; font-weight: bold; color: #667eea; margin: 10px 0; }}
            .kpi-label {{ color: #718096; font-size: 14px; text-transform: uppercase; }}
            .section {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; }}
            .estado-pendiente {{ color: #ecc94b; font-weight: bold; }}
            .estado-pagado {{ color: #48bb78; font-weight: bold; }}
            .logout {{ float: right; color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🤖 BotlyPro - {nombre_negocio}</h2>
            <a href="/admin/cliente-login" class="logout">Cerrar Sesión</a>
        </div>
        
        <div class="container">
            <h1>📊 Dashboard de Ventas</h1>
            
            <!-- KPIs -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">💰 Ventas Totales</div>
                    <div class="kpi-number">${stats['ventas_totales']:,}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">📦 Total Pedidos</div>
                    <div class="kpi-number">{stats['total_pedidos']}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">🧾 Ticket Promedio</div>
                    <div class="kpi-number">${stats['ticket_promedio']:,}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">👥 Clientes Únicos</div>
                    <div class="kpi-number">{stats['clientes_unicos']}</div>
                </div>
            </div>
            
            <!-- Últimos pedidos -->
            <div class="section">
                <h3>📋 Últimos Pedidos</h3>
                {generar_tabla_pedidos(stats['ultimos_pedidos'])}
            </div>
            
            <!-- Productos más vendidos -->
            <div class="section">
                <h3>🛍️ Productos Más Vendidos</h3>
                {generar_tabla_productos(stats['top_productos'])}
            </div>
            
            <!-- Cambiar contraseña -->
            <div class="section">
                <h3>🔐 Cambiar Contraseña</h3>
                <form method="POST" action="/admin/cliente-dashboard/{cliente_id}/cambiar-password" id="passwordForm">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; color: #4a5568;">Contraseña actual:</label>
                        <div style="position: relative; width: 300px;">
                            <input type="password" name="password_actual" id="pass_actual" required style="padding: 10px; width: 100%; border: 1px solid #e2e8f0; border-radius: 5px; box-sizing: border-box;">
                            <span onclick="togglePassword('pass_actual', 'eye1')" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 18px;" id="eye1">👁️</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; color: #4a5568;">Nueva contraseña:</label>
                        <div style="position: relative; width: 300px;">
                            <input type="password" name="password_nueva" id="pass_nueva" required style="padding: 10px; width: 100%; border: 1px solid #e2e8f0; border-radius: 5px; box-sizing: border-box;">
                            <span onclick="togglePassword('pass_nueva', 'eye2')" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 18px;" id="eye2">👁️</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; color: #4a5568;">Confirmar nueva contraseña:</label>
                        <div style="position: relative; width: 300px;">
                            <input type="password" name="password_confirmar" id="pass_confirmar" required style="padding: 10px; width: 100%; border: 1px solid #e2e8f0; border-radius: 5px; box-sizing: border-box;">
                            <span onclick="togglePassword('pass_confirmar', 'eye3')" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer; font-size: 18px;" id="eye3">👁️</span>
                        </div>
                    </div>
                    <button type="submit" style="background: #48bb78; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Cambiar Contraseña</button>
                </form>
            </div>
            
            <script>
                function togglePassword(inputId, eyeId) {{
                    const input = document.getElementById(inputId);
                    const eye = document.getElementById(eyeId);
                    if (input.type === "password") {{
                        input.type = "text";
                        eye.textContent = "🙈";
                    }} else {{
                        input.type = "password";
                        eye.textContent = "👁️";
                    }}
                }}
            </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

def obtener_estadisticas_cliente(cliente_id: str) -> dict:
    """Obtiene estadísticas de ventas para un cliente específico"""
    stats = {
        'ventas_totales': 0,
        'total_pedidos': 0,
        'ticket_promedio': 0,
        'clientes_unicos': 0,
        'ultimos_pedidos': [],
        'top_productos': []
    }
    
    try:
        from database.database_saas import db_saas
        conn = db_saas._get_connection()
        cursor = conn.cursor()
        
        # Ventas totales y total pedidos
        cursor.execute("""
            SELECT COUNT(*) as total, COALESCE(SUM(total), 0) as ventas,
                   COALESCE(AVG(total), 0) as promedio
            FROM pedidos WHERE cliente_id = ?
        """, (cliente_id,))
        row = cursor.fetchone()
        stats['total_pedidos'] = row['total'] or 0
        stats['ventas_totales'] = int(row['ventas'] or 0)
        stats['ticket_promedio'] = int(row['promedio'] or 0)
        
        # Clientes únicos
        cursor.execute("""
            SELECT COUNT(DISTINCT usuario_id) as unicos
            FROM pedidos WHERE cliente_id = ?
        """, (cliente_id,))
        stats['clientes_unicos'] = cursor.fetchone()['unicos'] or 0
        
        # Últimos pedidos
        cursor.execute("""
            SELECT numero_orden, total, estado, creado_en
            FROM pedidos WHERE cliente_id = ?
            ORDER BY creado_en DESC LIMIT 10
        """, (cliente_id,))
        stats['ultimos_pedidos'] = [dict(row) for row in cursor.fetchall()]
        
        # Top productos
        cursor.execute("""
            SELECT nombre_producto, COUNT(*) as cantidad
            FROM pedido_items pi
            JOIN pedidos p ON pi.pedido_id = p.id
            WHERE p.cliente_id = ?
            GROUP BY nombre_producto
            ORDER BY cantidad DESC LIMIT 5
        """, (cliente_id,))
        stats['top_productos'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
    except Exception as e:
        print(f"⚠️ Error obteniendo estadísticas: {e}")
    
    return stats

def generar_tabla_pedidos(pedidos: list) -> str:
    """Genera tabla HTML de pedidos"""
    if not pedidos:
        return "<p style='color: #718096;'>No hay pedidos registrados</p>"
    
    filas = ""
    for p in pedidos:
        estado_class = f"estado-{p['estado']}"
        filas += f"""
        <tr>
            <td>{p['numero_orden']}</td>
            <td>${p['total']:,}</td>
            <td class="{estado_class}">{p['estado'].upper()}</td>
            <td>{p['creado_en'][:10]}</td>
        </tr>
        """
    
    return f"""
    <table>
        <thead>
            <tr>
                <th>Número</th>
                <th>Total</th>
                <th>Estado</th>
                <th>Fecha</th>
            </tr>
        </thead>
        <tbody>{filas}</tbody>
    </table>
    """

def generar_tabla_productos(productos: list) -> str:
    """Genera tabla HTML de productos más vendidos"""
    if not productos:
        return "<p style='color: #718096;'>No hay datos de productos</p>"
    
    filas = ""
    for i, p in enumerate(productos, 1):
        filas += f"""
        <tr>
            <td>{i}</td>
            <td>{p['nombre_producto']}</td>
            <td>{p['cantidad']} ventas</td>
        </tr>
        """
    
    return f"""
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Producto</th>
                <th>Cantidad</th>
            </tr>
        </thead>
        <tbody>{filas}</tbody>
    </table>
    """

@router.post("/cliente-dashboard/{cliente_id}/cambiar-password")
async def cambiar_password_cliente(
    cliente_id: str,
    password_actual: str = Form(""),
    password_nueva: str = Form(""),
    password_confirmar: str = Form("")
):
    """Cambia la contraseña de un cliente"""
    try:
        # Verificar que el cliente existe
        config_path = Path(f"clientes/configs/{cliente_id}.json")
        if not config_path.exists():
            return HTMLResponse(content="<h1>❌ Cliente no encontrado</h1><a href='/admin/cliente-login'>Volver</a>")
        
        # Cargar configuración
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verificar contraseña actual
        password_guardada = config.get('password', f"{cliente_id}2024")
        if password_actual != password_guardada:
            return HTMLResponse(content="<h1>❌ Contraseña actual incorrecta</h1><a href='/admin/cliente-dashboard/{cliente_id}'>Volver</a>")
        
        # Verificar que las nuevas contraseñas coinciden
        if password_nueva != password_confirmar:
            return HTMLResponse(content="<h1>❌ Las contraseñas nuevas no coinciden</h1><a href='/admin/cliente-dashboard/{cliente_id}'>Volver</a>")
        
        # Guardar nueva contraseña
        config['password'] = password_nueva
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Contraseña Cambiada - BotlyPro</title></head>
        <body style="font-family: Arial; margin: 0; background: #f7fafc;">
            <div style="background: #2d3748; color: white; padding: 20px;">
                <h2>🤖 BotlyPro</h2>
            </div>
            <div style="max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #48bb78;">✅ Contraseña Actualizada</h1>
                <p>Tu contraseña ha sido cambiada exitosamente.</p>
                <br>
                <a href="/admin/cliente-dashboard/{cliente_id}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Volver al Dashboard</a>
            </div>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>❌ Error al cambiar contraseña</h1><p>{str(e)}</p><a href='/admin/cliente-dashboard/{cliente_id}'>Volver</a>")

@router.get("/cliente/{cliente_id}/toggle")
async def toggle_cliente_estado(cliente_id: str):
    """Activa o desactiva un cliente"""
    try:
        # No permitir desactivar publiya7
        if cliente_id == 'publiya7':
            return HTMLResponse(content="<h1>❌ No se puede desactivar el cliente principal</h1><a href='/admin/dashboard'>Volver</a>")
        
        # Cargar configuración
        config_path = Path(f"clientes/configs/{cliente_id}.json")
        if not config_path.exists():
            return HTMLResponse(content="<h1>❌ Cliente no encontrado</h1><a href='/admin/dashboard'>Volver</a>")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Cambiar estado
        estado_actual = config.get('estado', 'activo')
        nuevo_estado = 'inactivo' if estado_actual == 'activo' else 'activo'
        config['estado'] = nuevo_estado
        
        # Guardar
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    except Exception as e:
        return HTMLResponse(content=f"<h1>❌ Error al cambiar estado</h1><p>{str(e)}</p><a href='/admin/dashboard'>Volver</a>")

print("✅ Panel simple cargado")
