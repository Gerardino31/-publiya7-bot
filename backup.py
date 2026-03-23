"""
backup.py - Sistema de backup para la base de datos
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

class BackupManager:
    """Gestiona backups de la base de datos."""
    
    def __init__(self, db_path='database/pedidos.db', backup_dir='backups'):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def crear_backup(self) -> str:
        """Crea un backup de la base de datos con timestamp."""
        if not self.db_path.exists():
            print("[ERROR] Base de datos no encontrada")
            return None
        
        # Generar nombre con fecha y hora
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"pedidos_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"[OK] Backup creado: {backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f"[ERROR] Error creando backup: {e}")
            return None
    
    def listar_backups(self) -> list:
        """Lista todos los backups disponibles."""
        if not self.backup_dir.exists():
            return []
        
        backups = sorted(
            self.backup_dir.glob('pedidos_backup_*.db'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        return [str(b) for b in backups]
    
    def restaurar_backup(self, backup_path: str) -> bool:
        """Restaura la base de datos desde un backup."""
        backup = Path(backup_path)
        
        if not backup.exists():
            print(f"[ERROR] Backup no encontrado: {backup_path}")
            return False
        
        try:
            # Crear backup de seguridad antes de restaurar
            self.crear_backup()
            
            # Restaurar
            shutil.copy2(backup, self.db_path)
            print(f"[OK] Base de datos restaurada desde: {backup_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Error restaurando backup: {e}")
            return False
    
    def limpiar_backups_antiguos(self, dias=7):
        """Elimina backups más antiguos que X días."""
        from datetime import timedelta
        
        limite = datetime.now() - timedelta(days=dias)
        eliminados = 0
        
        for backup in self.backup_dir.glob('pedidos_backup_*.db'):
            fecha_backup = datetime.fromtimestamp(backup.stat().st_mtime)
            if fecha_backup < limite:
                backup.unlink()
                eliminados += 1
        
        print(f"[OK] {eliminados} backups antiguos eliminados")
        return eliminados


# Función helper para crear backup rápido
def backup_rapido():
    """Crea un backup rápido de la base de datos."""
    manager = BackupManager()
    return manager.crear_backup()


if __name__ == "__main__":
    print("="*70)
    print("SISTEMA DE BACKUP")
    print("="*70)
    
    manager = BackupManager()
    
    # Crear backup
    print("\n1. Creando backup...")
    backup = manager.crear_backup()
    
    if backup:
        print(f"   Backup creado: {backup}")
    
    # Listar backups
    print("\n2. Backups disponibles:")
    backups = manager.listar_backups()
    for i, b in enumerate(backups[:5], 1):  # Mostrar últimos 5
        print(f"   {i}. {Path(b).name}")
    
    print("\n" + "="*70)
    print("Backup completado")
    print("="*70)
