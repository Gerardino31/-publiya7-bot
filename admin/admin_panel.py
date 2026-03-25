"""
admin_panel.py - Panel de Administración BotlyPro (Simplificado)
Panel web básico para gestionar clientes
"""

import os
import sys
from pathlib import Path

# Agregar path raíz
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import json

# Crear router para el panel
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Usuario y contraseña del panel (temporal)
ADMIN_USER = "admin"
ADMIN_PASS = "botlypro2024"

# HTML del login
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - BotlyPro Admin</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #667eea; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .container {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); width: 300px; }}
        h1 {{ color: #667eea; text-align: center; margin-bottom: 30px; }}
        input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        button {{ width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
        button:hover {{ background: #5568d3; }}
        .error {{ color: red; text-align: center; margin-bottom: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 BotlyPro</h1>
        <h3 style="text-align: center; color: #666;">Panel de Administración</h3>
        {error_msg}
        <form method="POST" action="/admin/login">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
        </form>
    </div>
</body>
</html>
"""

# HTML del dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dashboard - BotlyPro</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f7fa; }}
        .sidebar {{ width: 250px; background: #2d3748; height: 100vh; position: fixed; color: white; padding: 20px; }}
        .sidebar h2 {{ color: #667eea; }}
        .sidebar a {{ display: block; color: #cbd5e0; text-decoration: none; padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .sidebar a:hover {{ background: #667eea; color: white; }}
        .main {{ margin-left: 290px; padding: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #667eea; color: white; }}
        .btn {{ background: #667eea; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>🤖 BotlyPro</h2>
        <a href="/admin/dashboard">📊 Dashboard</a>
        <a href="/admin/clientes">👥 Clientes</a>
        <a href="/admin/conversaciones">💬 Conversaciones</a>
    </div>
    <div class="main">
        <h1>Dashboard</h1>
        <div class="card">
            <h3>Total Clientes: {total_clientes}</h3>
        </div>
        <div class="card">
            <h2>Clientes Activos</h2>
            <table>
                <tr><th>ID</th><th>Nombre</th><th>Teléfono</th><th>Acciones</th></tr>
                {clientes_rows}
            </table>
        </div>
    </div>
</body>
</html>
"""

@admin_router.get("/", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Página de login"""
    return HTMLResponse(content=LOGIN_HTML.format(error_msg=""))

@admin_router.post("/login")
async def admin_login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    """Procesar login"""
    if username == ADMIN_USER and password == ADMIN_PASS:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    error_html = '<div class="error">Credenciales incorrectas</div>'
    return HTMLResponse(content=LOGIN_HTML.format(error_msg=error_html))

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard principal"""
    # Cargar clientes
    clientes_dir = Path("clientes/configs")
    clientes = []
    
    if clientes_dir.exists():
        for config_file in clientes_dir.glob("*.json"):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                clientes.append(config)
    
    # Generar filas de la tabla (solo clientes con ID válido)
    rows = ""
    for c in clientes:
        cliente_id = c.get('cliente_id', '')
        nombre = c.get('nombre', c.get('nombre_empresa', 'Sin nombre'))
        telefono = c.get('telefono', 'N/A')
        
        # Solo mostrar si tiene cliente_id
        if cliente_id:
            rows += f"<tr><td>{cliente_id}</td><td>{nombre}</td><td>{telefono}</td><td><a href='/admin/cliente/{cliente_id}' class='btn'>Ver</a></td></tr>"
    
    html = DASHBOARD_HTML.format(
        total_clientes=len(clientes),
        clientes_rows=rows
    )
    
    return HTMLResponse(content=html)

@admin_router.get("/clientes", response_class=HTMLResponse)
async def admin_clientes(request: Request):
    """Lista de clientes"""
    return RedirectResponse(url="/admin/dashboard")

@admin_router.get("/cliente/{cliente_id}", response_class=HTMLResponse)
async def ver_cliente(request: Request, cliente_id: str):
    """Ver detalles de un cliente"""
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    
    if not config_path.exists():
        return HTMLResponse(content="<h1>Cliente no encontrado</h1><a href='/admin/dashboard'>Volver</a>")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Campos editables básicos
    nombre = config.get('nombre', '')
    telefono = config.get('telefono', '')
    email = config.get('email', '')
    eslogan = config.get('eslogan', '')
    
    # Mensajes del bot
    mensajes = config.get('mensajes', {})
    bienvenida = mensajes.get('bienvenida', '')
    despedida = mensajes.get('despedida', '')
    
    # Productos (categorías principales) - Manejar como diccionario
    categorias_dict = config.get('categorias', {})
    if isinstance(categorias_dict, dict):
        # Convertir diccionario a lista para mostrar
        categorias_list = []
        for cat_key, cat_data in categorias_dict.items():
            if isinstance(cat_data, dict):
                cat_data['id'] = cat_key
                categorias_list.append(cat_data)
    else:
        categorias_list = []
    
    productos_html = ""
    for i, cat in enumerate(categorias_list[:5]):  # Mostrar máximo 5 categorías
        nombre_cat = cat.get('nombre', '')
        cat_id = cat.get('id', f'cat_{i}')
        productos_html += f'<div class="form-group"><label>Categoría {i+1}</label><input type="text" name="categoria_{i}" value="{nombre_cat}"><input type="hidden" name="categoria_id_{i}" value="{cat_id}"></div>'
    
    # Frases de cortesía
    frases = config.get('frases_cortesia', {})
    frase_general = frases.get('general', '¡Gracias por contactarnos!')
    frase_despedida = frases.get('despedida', '¡Que tengas un excelente día!')
    
    # Precios - deshabilitado temporalmente
    precios_html = ""
    
    # Respuestas automáticas (FAQ)
    faq = config.get('faq', {})
    faq_horario = faq.get('horario', 'Lunes a Viernes 8am - 6pm, Sábados 9am - 1pm')
    faq_ubicacion = faq.get('ubicacion', 'Estamos ubicados en el centro de la ciudad')
    faq_error = faq.get('no_entendi', 'Lo siento, no entendí tu mensaje. ¿Podrías reformularlo?')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Cliente {cliente_id} - BotlyPro</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f7fa; }}
            .sidebar {{ width: 250px; background: #2d3748; height: 100vh; position: fixed; color: white; padding: 20px; }}
            .sidebar h2 {{ color: #667eea; }}
            .sidebar a {{ display: block; color: #cbd5e0; text-decoration: none; padding: 10px; margin: 5px 0; border-radius: 5px; }}
            .sidebar a:hover {{ background: #667eea; color: white; }}
            .main {{ margin-left: 290px; padding: 30px; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #333; }}
            input[type="text"], input[type="email"] {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            .btn {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px; border: none; cursor: pointer; }}
            .btn-secondary {{ background: #718096; margin-left: 10px; }}
            .success {{ background: #c6f6d5; color: #22543d; padding: 10px; border-radius: 5px; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>🤖 BotlyPro</h2>
            <a href="/admin/dashboard">📊 Dashboard</a>
            <a href="/admin/clientes">👥 Clientes</a>
            <a href="/admin/conversaciones">💬 Conversaciones</a>
        </div>
        <div class="main">
            <h1>Editar Cliente: {nombre}</h1>
            <div class="card">
                <form method="POST" action="/admin/cliente/{cliente_id}/guardar">
                    <div class="form-group">
                        <label>Nombre del Negocio</label>
                        <input type="text" name="nombre" value="{nombre}" required>
                    </div>
                    <div class="form-group">
                        <label>Teléfono</label>
                        <input type="text" name="telefono" value="{telefono}">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email" value="{email}">
                    </div>
                    <div class="form-group">
                        <label>Eslogan</label>
                        <input type="text" name="eslogan" value="{eslogan}">
                    </div>
                    <div class="form-group">
                        <label>Mensaje de Bienvenida del Bot</label>
                        <input type="text" name="bienvenida" value="{bienvenida}" placeholder="Ej: ¡Hola! Bienvenido a nuestra imprenta...">
                    </div>
                    <div class="form-group">
                        <label>Mensaje de Despedida del Bot</label>
                        <input type="text" name="despedida" value="{despedida}" placeholder="Ej: Gracias por contactarnos. ¡Hasta pronto!">
                    </div>
                    <hr style="margin: 20px 0;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">📦 Categorías de Productos</h3>
                    {productos_html}
                    <hr style="margin: 20px 0;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">💬 Frases de Cortesía</h3>
                    <div class="form-group">
                        <label>Frase General</label>
                        <input type="text" name="frase_general" value="{frase_general}" placeholder="Ej: ¡Gracias por contactarnos!">
                    </div>
                    <div class="form-group">
                        <label>Frase de Despedida</label>
                        <input type="text" name="frase_despedida" value="{frase_despedida}" placeholder="Ej: ¡Que tengas un excelente día!">
                    </div>
                    {precios_html}
                    <hr style="margin: 20px 0;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">❓ Respuestas Automáticas (FAQ)</h3>
                    <div class="form-group">
                        <label>Respuesta a "horario"</label>
                        <input type="text" name="faq_horario" value="{faq_horario}" placeholder="Ej: Lunes a Viernes 8am - 6pm">
                    </div>
                    <div class="form-group">
                        <label>Respuesta a "ubicación/dirección"</label>
                        <input type="text" name="faq_ubicacion" value="{faq_ubicacion}" placeholder="Ej: Estamos en el centro de la ciudad">
                    </div>
                    <div class="form-group">
                        <label>Mensaje cuando no entiende</label>
                        <input type="text" name="faq_error" value="{faq_error}" placeholder="Ej: Lo siento, no entendí. ¿Podrías reformularlo?">
                    </div>
                    <button type="submit" class="btn">Guardar Cambios</button>
                    <a href="/admin/dashboard" class="btn btn-secondary">Cancelar</a>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@admin_router.post("/cliente/{cliente_id}/guardar")
async def guardar_cliente(
    request: Request,
    cliente_id: str,
    nombre: str = Form(...),
    telefono: str = Form(""),
    email: str = Form(""),
    eslogan: str = Form(""),
    bienvenida: str = Form(""),
    despedida: str = Form(""),
    categoria_0: str = Form(""),
    categoria_1: str = Form(""),
    categoria_2: str = Form(""),
    categoria_3: str = Form(""),
    categoria_4: str = Form(""),
    categoria_id_0: str = Form(""),
    categoria_id_1: str = Form(""),
    categoria_id_2: str = Form(""),
    categoria_id_3: str = Form(""),
    categoria_id_4: str = Form(""),
    frase_general: str = Form(""),
    frase_despedida: str = Form(""),
    faq_horario: str = Form(""),
    faq_ubicacion: str = Form(""),
    faq_error: str = Form(""),
):
    """Guardar cambios de un cliente"""
    try:
        config_path = Path(f"clientes/configs/{cliente_id}.json")
        
        if not config_path.exists():
            return HTMLResponse(content="<h1>Cliente no encontrado</h1><a href='/admin/dashboard'>Volver</a>")
        
        # Leer configuración actual
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Actualizar campos básicos
        config['nombre'] = nombre
        config['telefono'] = telefono
        config['email'] = email
        config['eslogan'] = eslogan
        
        # Actualizar mensajes del bot
        if 'mensajes' not in config:
            config['mensajes'] = {}
        config['mensajes']['bienvenida'] = bienvenida
        config['mensajes']['despedida'] = despedida
        
        # Actualizar frases de cortesía
        if 'frases_cortesia' not in config:
            config['frases_cortesia'] = {}
        config['frases_cortesia']['general'] = frase_general
        config['frases_cortesia']['despedida'] = frase_despedida
        
        # Actualizar categorías (manejar como diccionario)
        categorias_dict = config.get('categorias', {})
        if not isinstance(categorias_dict, dict):
            categorias_dict = {}
        
        # Obtener IDs de categorías del formulario
        cat_ids = [categoria_id_0, categoria_id_1, categoria_id_2, categoria_id_3, categoria_id_4]
        cat_nombres = [categoria_0, categoria_1, categoria_2, categoria_3, categoria_4]
        
        for i, (cat_id, cat_nombre) in enumerate(zip(cat_ids, cat_nombres)):
            if cat_nombre.strip() and cat_id:
                # Si existe la categoría, actualizar nombre
                if cat_id in categorias_dict:
                    if isinstance(categorias_dict[cat_id], dict):
                        categorias_dict[cat_id]['nombre'] = cat_nombre
                else:
                    # Crear nueva categoría
                    categorias_dict[f'cat_nueva_{i}'] = {
                        'nombre': cat_nombre,
                        'tipos': []
                    }
        
        config['categorias'] = categorias_dict
        
        # Actualizar FAQ
        if 'faq' not in config:
            config['faq'] = {}
        config['faq']['horario'] = faq_horario
        config['faq']['ubicacion'] = faq_ubicacion
        config['faq']['no_entendi'] = faq_error
        
        # Guardar
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # Redirigir con mensaje de éxito
        return RedirectResponse(url=f"/admin/cliente/{cliente_id}?success=1", status_code=302)
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}<br><pre>{traceback.format_exc()}</pre>"
        return HTMLResponse(content=f"<h1>Error al guardar</h1><p>{error_msg}</p><a href='/admin/cliente/{cliente_id}'>Volver</a>")

@admin_router.get("/conversaciones", response_class=HTMLResponse)
async def admin_conversaciones(request: Request):
    """Ver conversaciones"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Conversaciones - BotlyPro</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fa; }
            .sidebar { width: 250px; background: #2d3748; height: 100vh; position: fixed; color: white; padding: 20px; }
            .sidebar h2 { color: #667eea; }
            .sidebar a { display: block; color: #cbd5e0; text-decoration: none; padding: 10px; margin: 5px 0; border-radius: 5px; }
            .sidebar a:hover { background: #667eea; color: white; }
            .main { margin-left: 290px; padding: 30px; }
            .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2>🤖 BotlyPro</h2>
            <a href="/admin/dashboard">📊 Dashboard</a>
            <a href="/admin/clientes">👥 Clientes</a>
            <a href="/admin/conversaciones">💬 Conversaciones</a>
        </div>
        <div class="main">
            <h1>Conversaciones</h1>
            <div class="card">
                <p>Próximamente: Aquí se mostrarán las conversaciones en tiempo real.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

print("✅ Panel de administración BotlyPro cargado correctamente")
