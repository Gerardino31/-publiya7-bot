"""
dashboard_api.py - API de métricas para Dashboard IA vs Reglas

Endpoints para el panel de analytics.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

DB_PATH = Path(__file__).parent.parent / "botlypro_logs.db"

def get_db_connection():
    """Obtiene conexión a la BD de logs"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/resumen")
async def get_resumen():
    """Resumen general del dashboard"""
    try:
        # Si la BD no existe, retornar valores por defecto
        if not DB_PATH.exists():
            return {
                "ventas_hoy": 0,
                "conversaciones_hoy": 0,
                "total_decisiones": 0,
                "ia_vs_reglas": {
                    "ia": 0,
                    "reglas": 0,
                    "porcentaje_ia": 0
                }
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ventas hoy (simulado - necesitarías unir con tabla pedidos)
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        # Total de decisiones registradas
        cursor.execute("SELECT COUNT(*) as total FROM logs_decisiones")
        total_decisiones = cursor.fetchone()['total']
        
        # Decisiones IA vs Reglas (basado en qué tomó la decisión final)
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN decision_ia IS NOT NULL THEN 1 ELSE 0 END) as con_ia,
                SUM(CASE WHEN decision_ia IS NULL THEN 1 ELSE 0 END) as solo_reglas
            FROM logs_decisiones
        """)
        row = cursor.fetchone()
        con_ia = row['con_ia'] or 0
        solo_reglas = row['solo_reglas'] or 0
        
        total = con_ia + solo_reglas
        porcentaje_ia = (con_ia / total * 100) if total > 0 else 0
        
        # Conversaciones únicas hoy
        cursor.execute("""
            SELECT COUNT(DISTINCT usuario_id) as conversaciones 
            FROM logs_decisiones 
            WHERE DATE(created_at) = ?
        """, (hoy,))
        conversaciones_hoy = cursor.fetchone()['conversaciones'] or 0
        
        conn.close()
        
        return {
            "ventas_hoy": 0,  # TODO: Unir con tabla pedidos
            "conversaciones_hoy": conversaciones_hoy,
            "total_decisiones": total_decisiones,
            "ia_vs_reglas": {
                "ia": con_ia,
                "reglas": solo_reglas,
                "porcentaje_ia": round(porcentaje_ia, 1)
            }
        }
    except Exception as e:
        # En caso de error, retornar estructura válida
        return {
            "ventas_hoy": 0,
            "conversaciones_hoy": 0,
            "total_decisiones": 0,
            "ia_vs_reglas": {
                "ia": 0,
                "reglas": 0,
                "porcentaje_ia": 0
            },
            "error": str(e)
        }

@router.get("/decisiones")
async def get_decisiones(limit: int = 50):
    """Últimas decisiones registradas"""
    try:
        if not DB_PATH.exists():
            return {"decisiones": []}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                usuario_id,
                cliente_id,
                mensaje,
                decision_reglas,
                decision_ia,
                decision_final,
                created_at
            FROM logs_decisiones
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        decisiones = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {"decisiones": decisiones}
    except Exception as e:
        return {"decisiones": [], "error": str(e)}

@router.get("/ia")
async def get_ia_metrics():
    """Métricas específicas de IA"""
    try:
        if not DB_PATH.exists():
            return {
                "precision_estimada": 0,
                "total_comparaciones": 0,
                "coincidencias": 0,
                "top_decisiones_ia": []
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Precisión estimada (cuántas veces IA y reglas coinciden)
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN decision_reglas = decision_ia THEN 1 ELSE 0 END) as coincidencias
            FROM logs_decisiones
            WHERE decision_ia IS NOT NULL
        """)
        row = cursor.fetchone()
        
        total = row['total'] or 0
        coincidencias = row['coincidencias'] or 0
        precision = (coincidencias / total * 100) if total > 0 else 0
        
        # Tipos de decisiones más comunes de IA
        cursor.execute("""
            SELECT decision_ia, COUNT(*) as count
            FROM logs_decisiones
            WHERE decision_ia IS NOT NULL
            GROUP BY decision_ia
            ORDER BY count DESC
            LIMIT 5
        """)
        
        top_decisiones = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "precision_estimada": round(precision, 1),
            "total_comparaciones": total,
            "coincidencias": coincidencias,
            "top_decisiones_ia": top_decisiones
        }
    except Exception as e:
        return {
            "precision_estimada": 0,
            "total_comparaciones": 0,
            "coincidencias": 0,
            "top_decisiones_ia": [],
            "error": str(e)
        }

@router.get("/conversaciones-activas")
async def get_conversaciones_activas():
    """Conversaciones de las últimas 24 horas"""
    try:
        if not DB_PATH.exists():
            return {"conversaciones_activas": []}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        ultimas_24h = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            SELECT DISTINCT usuario_id, cliente_id, MAX(created_at) as ultima_actividad
            FROM logs_decisiones
            WHERE created_at > ?
            GROUP BY usuario_id, cliente_id
            ORDER BY ultima_actividad DESC
            LIMIT 20
        """, (ultimas_24h,))
        
        conversaciones = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {"conversaciones_activas": conversaciones}
    except Exception as e:
        return {"conversaciones_activas": [], "error": str(e)}
