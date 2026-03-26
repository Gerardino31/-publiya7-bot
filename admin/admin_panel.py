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
    
    # Categorías (mostrar nombres)
    categorias_dict = config.get('categorias', {})
    cat_nombres = []
    if isinstance(categorias_dict, dict):
        for cat_key, cat_data in categorias_dict.items():
            if isinstance(cat_data, dict):
                cat_nombres.append(cat_data.get('nombre', cat_key))
    
    # Generar HTML de categorías
    cats_html = ""
    for i, cat_nombre in enumerate(cat_nombres[:5]):
        cats_html += f'<div style="margin-bottom: 10px;"><label style="font-weight: bold;">Categoría {i+1}:</label> {cat_nombre}</div>'
    
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
                <h3 style="color: #667eea;">📦 Categorías de Productos</h3>
                {cats_html}
                <p style="color: #666; font-size: 12px;">* Para editar productos y precios, contactar soporte</p>
                <button type="submit" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Guardar</button>
                <a href="/admin/dashboard" style="background: #718096; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Volver</a>
                <a href="/admin/cliente/{cliente_id}/productos" style="background: #48bb78; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">📦 Ver Productos</a>
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
                form_html += f"<h3 style='color: #667eea; margin-top: 20px;'>📦 {cat_nombre}</h3>"
                
                # Mostrar productos editables
                tipos = cat_data.get('tipos', [])
                for tipo in tipos[:3]:  # Máximo 3 productos por categoría
                    if isinstance(tipo, dict):
                        prod_id = tipo.get('id', f'prod_{prod_idx}')
                        prod_nombre = tipo.get('nombre', 'Sin nombre')
                        precio_1000 = tipo.get('precio_1000', 0)
                        form_html += f"""
                        <div style="margin-bottom: 10px; padding: 10px; background: #f7fafc; border-radius: 5px;">
                            <label style="font-weight: bold;">{prod_nombre}</label><br>
                            <input type="hidden" name="prod_id_{prod_idx}" value="{cat_key}|{prod_id}">
                            Precio 1000 unid: $<input type="number" name="precio_{prod_idx}" value="{precio_1000}" style="padding: 5px; width: 100px;">
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
                <button type="submit" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px;">Guardar Precios</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.post("/cliente/{cliente_id}/productos/guardar")
async def guardar_productos(
    cliente_id: str,
    prod_id_0: str = Form(""),
    prod_id_1: str = Form(""),
    prod_id_2: str = Form(""),
    prod_id_3: str = Form(""),
    prod_id_4: str = Form(""),
    prod_id_5: str = Form(""),
    precio_0: int = Form(0),
    precio_1: int = Form(0),
    precio_2: int = Form(0),
    precio_3: int = Form(0),
    precio_4: int = Form(0),
    precio_5: int = Form(0),
):
    try:
        config_path = Path(f"clientes/configs/{cliente_id}.json")
        
        if not config_path.exists():
            return HTMLResponse(content="<h1>Cliente no encontrado</h1>")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Actualizar precios
        prod_ids = [prod_id_0, prod_id_1, prod_id_2, prod_id_3, prod_id_4, prod_id_5]
        precios = [precio_0, precio_1, precio_2, precio_3, precio_4, precio_5]
        
        for prod_id_str, nuevo_precio in zip(prod_ids, precios):
            if prod_id_str and "|" in prod_id_str:
                cat_key, prod_id = prod_id_str.split("|")
                if cat_key in config.get('categorias', {}):
                    cat_data = config['categorias'][cat_key]
                    if isinstance(cat_data, dict):
                        for tipo in cat_data.get('tipos', []):
                            if isinstance(tipo, dict) and tipo.get('id') == prod_id:
                                tipo['precio_1000'] = nuevo_precio
                                break
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return RedirectResponse(url=f"/admin/cliente/{cliente_id}/productos", status_code=302)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error al guardar</h1><p>{str(e)}</p><a href='/admin/cliente/{cliente_id}/productos'>Volver</a>")

print("✅ Panel simple cargado")
