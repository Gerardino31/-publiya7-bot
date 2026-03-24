"""
admin_panel.py - Panel de Administración BotlyPro
Panel web para gestionar clientes y configuraciones
"""

import os
import sys
from pathlib import Path

# Agregar path raíz
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path

# Crear router para el panel
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Configurar templates - usar path absoluto
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Usuario y contraseña del panel (temporal - luego en BD)
ADMIN_USER = "admin"
ADMIN_PASS = "botlypro2024"

@admin_router.get("/", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Página de login del panel"""
    return templates.TemplateResponse("login.html", {"request": request})

@admin_router.post("/login")
async def admin_login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    """Procesar login"""
    if username == ADMIN_USER and password == ADMIN_PASS:
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales incorrectas"})

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard principal"""
    # Cargar lista de clientes
    clientes_dir = Path("clientes/configs")
    clientes = []
    
    if clientes_dir.exists():
        for config_file in clientes_dir.glob("*.json"):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                clientes.append({
                    'id': config.get('cliente_id', ''),
                    'nombre': config.get('nombre', ''),
                    'telefono': config.get('telefono', ''),
                    'ciudad': config.get('ciudad', '')
                })
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "clientes": clientes,
        "total_clientes": len(clientes)
    })

@admin_router.get("/cliente/{cliente_id}", response_class=HTMLResponse)
async def ver_cliente(request: Request, cliente_id: str):
    """Ver detalles de un cliente"""
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return templates.TemplateResponse("cliente.html", {
        "request": request,
        "cliente": config
    })

@admin_router.post("/cliente/{cliente_id}/guardar")
async def guardar_cliente(request: Request, cliente_id: str, config_data: str = Form(...)):
    """Guardar configuración de cliente"""
    config_path = Path(f"clientes/configs/{cliente_id}.json")
    
    try:
        # Validar JSON
        config = json.loads(config_data)
        
        # Guardar
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return {"status": "ok", "message": "Configuración guardada"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "JSON inválido"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@admin_router.get("/conversaciones", response_class=HTMLResponse)
async def ver_conversaciones(request: Request):
    """Ver todas las conversaciones"""
    from database import db
    
    # Obtener conversaciones recientes
    conversaciones = db.obtener_conversaciones_recientes(limit=50)
    
    return templates.TemplateResponse("conversaciones.html", {
        "request": request,
        "conversaciones": conversaciones
    })

print("✅ Panel de administración cargado")
