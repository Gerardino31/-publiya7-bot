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
    # Contar clientes
    clientes_dir = Path("clientes/configs")
    total = len(list(clientes_dir.glob("*.json"))) if clientes_dir.exists() else 0
    
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
            <p>Total Clientes: {total}</p>
            <p>Panel en construcción...</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

print("✅ Panel simple cargado")
