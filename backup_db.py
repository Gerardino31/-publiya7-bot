"""
backup_db.py - Script de backup de base de datos
Ejecutar: python backup_db.py
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configuración
DB_PATH = Path("database/pedidos.db")
BACKUP_DIR = Path("backups")
RETENTION_DAYS = 7  # Mantener backups de últimos 7 días

def crear_backup():
    """Crea un backup de la base de datos con timestamp."""
    
    if not DB_PATH.exists():
        print(f"[ERROR] Base de datos no encontrada: {DB_PATH}")
        return False
    
    # Crear directorio de backups si no existe
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre de backup con fecha
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"pedidos_backup_{timestamp}.db"
    
    try:
        # Copiar base de datos
        shutil.copy2(DB_PATH, backup_file)
        print(f"[OK] Backup creado: {backup_file}")
        
        # Limpiar backups antiguos
        limpiar_backups_antiguos()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creando backup: {e}")
        return False

def limpiar_backups_antiguos():
    """Elimina backups más antiguos que RETENTION_DAYS."""
    
    if not BACKUP_DIR.exists():
        return
    
    ahora = datetime.now()
    eliminados = 0
    
    for backup_file in BACKUP_DIR.glob("pedidos_backup_*.db"):
        # Obtener fecha del archivo
        fecha_archivo = datetime.fromtimestamp(backup_file.stat().st_mtime)
        dias_antiguedad = (ahora - fecha_archivo).days
        
        if dias_antiguedad > RETENTION_DAYS:
            backup_file.unlink()
            eliminados += 1
            print(f"[INFO] Backup antiguo eliminado: {backup_file.name}")
    
    if eliminados > 0:
        print(f"[OK] {eliminados} backups antiguos eliminados")

def listar_backups():
    """Lista todos los backups disponibles."""
    
    if not BACKUP_DIR.exists():
        print("[INFO] No hay directorio de backups")
        return
    
    backups = list(BACKUP_DIR.glob("pedidos_backup_*.db"))
    
    if not backups:
        print("[INFO] No hay backups disponibles")
        return
    
    print("\n" + "="*70)
    print("BACKUPS DISPONIBLES")
    print("="*70)
    
    for backup in sorted(backups, reverse=True):
        size_mb = backup.stat().st_size / (1024 * 1024)
        fecha = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  {backup.name:30} {size_mb:6.2f} MB   {fecha.strftime('%Y-%m-%d %H:%M')}")
    
    print("="*70)

def restaurar_backup(nombre_backup: str):
    """Restaura un backup específico."""
    
    backup_file = BACKUP_DIR / nombre_backup
    
    if not backup_file.exists():
        print(f"[ERROR] Backup no encontrado: {nombre_backup}")
        return False
    
    # Crear backup de la actual antes de restaurar
    if DB_PATH.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_actual = BACKUP_DIR / f"pedidos_pre_restauracion_{timestamp}.db"
        shutil.copy2(DB_PATH, backup_actual)
        print(f"[OK] Backup de seguridad creado: {backup_actual.name}")
    
    try:
        # Restaurar backup
        shutil.copy2(backup_file, DB_PATH)
        print(f"[OK] Base de datos restaurada desde: {nombre_backup}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error restaurando backup: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup de base de datos')
    parser.add_argument('--listar', '-l', action='store_true', help='Listar backups')
    parser.add_argument('--restaurar', '-r', type=str, help='Restaurar backup específico')
    
    args = parser.parse_args()
    
    if args.listar:
        listar_backups()
    elif args.restaurar:
        restaurar_backup(args.restaurar)
    else:
        # Crear backup por defecto
        print("="*70)
        print("BACKUP DE BASE DE DATOS")
        print("="*70)
        
        if crear_backup():
            print("\n[OK] Proceso completado exitosamente")
        else:
            print("\n[ERROR] El proceso falló")
        
        print("="*70)
