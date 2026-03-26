"""
admin_panel.py - Panel de Administración BotlyPro (Versión Simple)
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
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
async def login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return HTMLResponse(content="<h1>Error</h1><a href='/admin'>Volver</a>")

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
                            'telefono': config.get('telefono', 'N/A')
                        })
            except:
                pass
    
    # Generar filas de la tabla
    filas = ""
    for c in clientes:
        filas += f"<tr><td>{c['id']}</td><td>{c['nombre']}</td><td>{c['telefono']}</td><td><a href='/admin/cliente/{c['id']}' style='background: #667eea; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;'>Ver</a></td></tr>"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Dashboard - BotlyPro</title></head>
    <body style="font-family: Arial; margin: 0;">
        <div style="background: #2d3748; color: white; padding: 20px;">
            <h2>🤖 BotlyPro</h2>
        </div>
        <div style="padding: 30px;">
            <h1>Dashboard</h1>
            <p>Total Clientes: {len(clientes)}</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr style="background: #667eea; color: white;">
                    <th style="padding: 10px; text-align: left;">ID</th>
                    <th style="padding: 10px; text-align: left;">Nombre</th>
                    <th style="padding: 10px; text-align: left;">Teléfono</th>
                    <th style="padding: 10px; text-align: left;">Acción</th>
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
    bienvenida = mensajes.get('bienvenida', '')
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
                    <label style="display: block; font-weight: bold;">Mensaje de Bienvenida:</label>
                    <input type="text" name="bienvenida" value="{bienvenida}" style="padding: 8px; width: 300px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label style="display: block; font-weight: bold;">Mensaje de Despedida:</label>
                    <input type="text" name="despedida" value="{despedida}" style="padding: 8px; width: 300px;">
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
async def guardar_cliente(cliente_id: str, nombre: str = Form(...), telefono: str = Form(""), email: str = Form(""), eslogan: str = Form(""), bienvenida: str = Form(""), despedida: str = Form(""), frase_general: str = Form(""), frase_despedida: str = Form(""), faq_horario: str = Form(""), faq_ubicacion: str = Form(""), faq_error: str = Form("")):
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
    config['mensajes']['bienvenida'] = bienvenida
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
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
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
                        
                        # Detectar tipo de precio
                        if 'precio_1000' in tipo:
                            precio_val = tipo.get('precio_1000', 0)
                            precio_label = "Precio 1000 unid: $"
                            precio_field = f'<input type="number" name="prod_precio_{prod_idx}" value="{precio_val}" style="padding: 5px; width: 100px;">'
                        elif 'precio_cm2_con_terminado' in tipo:
                            precio_val = tipo.get('precio_cm2_con_terminado', 0)
                            precio_label = "Precio cm2 c/terminado: $"
                            precio_field = f'<input type="number" name="prod_precio_cm2_{prod_idx}" value="{precio_val}" style="padding: 5px; width: 100px;">'
                        elif 'precio_cm2_sin_terminado' in tipo:
                            precio_val = tipo.get('precio_cm2_sin_terminado', 0)
                            precio_label = "Precio cm2 s/terminado: $"
                            precio_field = f'<input type="number" name="prod_precio_cm2_{prod_idx}" value="{precio_val}" style="padding: 5px; width: 100px;">'
                        elif 'precio_cm2' in tipo:
                            precio_val = tipo.get('precio_cm2', 0)
                            precio_label = "Precio por cm2: $"
                            precio_field = f'<input type="number" name="prod_precio_cm2_{prod_idx}" value="{precio_val}" style="padding: 5px; width: 100px;">'
                        else:
                            # Buscar cualquier campo de precio
                            precio_val = 0
                            precio_label = "Precio: $"
                            for key in tipo.keys():
                                if 'precio' in key.lower():
                                    precio_val = tipo.get(key, 0)
                                    precio_label = f"{key.replace('_', ' ').title()}: $"
                                    break
                            precio_field = f'<input type="number" name="prod_precio_{prod_idx}" value="{precio_val}" style="padding: 5px; width: 100px;">'
                        
                        # Agregar step="0.1" para permitir decimales
                        precio_field_con_step = precio_field.replace('type="number"', 'type="number" step="0.1"')
                        
                        form_html += f"""
                        <div style="margin-bottom: 10px; padding: 10px; background: #f7fafc; border-radius: 5px; margin-left: 20px;">
                            <input type="hidden" name="prod_cat_{prod_idx}" value="{cat_key}">
                            <input type="hidden" name="prod_id_{prod_idx}" value="{prod_id}">
                            <label style="font-weight: bold;">Producto:</label>
                            <input type="text" name="prod_nombre_{prod_idx}" value="{prod_nombre}" style="padding: 5px; width: 250px; margin: 0 10px;">
                            <label>{precio_label}</label>
                            {precio_field_con_step}
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

print("✅ Panel simple cargado")
