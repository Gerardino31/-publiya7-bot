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
        body { font-family: Arial, sans-serif; background: #667eea; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); width: 300px; }
        h1 { color: #667eea; text-align: center; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #5568d3; }
        .error { color: red; text-align: center; margin-bottom: 15px; }
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
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f7fa; }
        .sidebar { width: 250px; background: #2d3748; height: 100vh; position: fixed; color: white; padding: 20px; }
        .sidebar h2 { color: #667eea; }
        .sidebar a { display: block; color: #cbd5e0; text-decoration: none; padding: 10px; margin: 5px 0; border-radius: 5px; }
        .sidebar a:hover { background: #667eea; color: white; }
        .main { margin-left: 290px; padding: 30px; }
        .card { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #667eea; color: white; }
        .btn { background: #667eea; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; }
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
    
    # Generar filas de la tabla
    rows = ""
    for c in clientes:
        rows += f"<tr><td>{c.get('cliente_id', '')}</td><td>{c.get('nombre', '')}</td><td>{c.get('telefono', '')}</td><td><a href='/admin/cliente/{c.get('cliente_id')}' class='btn'>Ver</a></td></tr>"
    
    html = DASHBOARD_HTML.format(
        total_clientes=len(clientes),
        clientes_rows=rows
    )
    
    return HTMLResponse(content=html)

@admin_router.get("/clientes", response_class=HTMLResponse)
async def admin_clientes(request: Request):
    """Lista de clientes"""
    return RedirectResponse(url="/admin/dashboard")

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

print("✅ Panel de administración simplificado cargado")
