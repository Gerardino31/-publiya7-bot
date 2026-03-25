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
                <button type="submit" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Guardar</button>
                <a href="/admin/dashboard" style="background: #718096; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Volver</a>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.post("/cliente/{cliente_id}/guardar")
async def guardar_cliente(cliente_id: str, nombre: str = Form(...), telefono: str = Form(""), email: str = Form(""), eslogan: str = Form(""), bienvenida: str = Form(""), despedida: str = Form("")):
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
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return RedirectResponse(url=f"/admin/cliente/{cliente_id}", status_code=302)

print("✅ Panel simple cargado")
