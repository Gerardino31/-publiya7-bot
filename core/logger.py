"""
core/logger.py - Sistema de logging para decisiones (Fase 1)

Guarda comparativas entre decisiones de reglas vs OpenClaw.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "botlypro_logs.db"

def init_logs_db():
    """Inicializa la base de datos de logs si no existe"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_decisiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id TEXT,
                cliente_id TEXT,
                mensaje TEXT,
                decision_reglas TEXT,
                decision_ia TEXT,
                decision_final TEXT,
                paso_bot INTEGER,
                categoria TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos de logs inicializada")
    except Exception as e:
        print(f"[INIT LOGS ERROR] {e}")

def guardar_evento(data):
    """
    Guarda un evento de decisión en la base de datos.
    
    Args:
        data: dict con:
            - usuario_id
            - cliente_id
            - mensaje
            - decision_reglas
            - decision_ia
            - decision_final
            - paso_bot (opcional)
            - categoria (opcional)
    """
    try:
        # Asegurar que la tabla existe
        init_logs_db()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO logs_decisiones (
                usuario_id,
                cliente_id,
                mensaje,
                decision_reglas,
                decision_ia,
                decision_final,
                paso_bot,
                categoria
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("usuario_id"),
            data.get("cliente_id"),
            data.get("mensaje"),
            data.get("decision_reglas"),
            data.get("decision_ia"),
            data.get("decision_final"),
            data.get("paso_bot"),
            data.get("categoria")
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"[LOG ERROR] {e}")
        # No propagar error para no afectar el flujo principal
