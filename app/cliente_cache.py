"""
cliente_cache.py - Sistema de cache dinámico para clientes SaaS
Detecta nuevos clientes automáticamente sin reiniciar
"""

import time
import json
from typing import Dict, Optional
from pathlib import Path
from database.database_saas import db_saas

class ClienteCache:
    """Cache dinámico de clientes con TTL de 60 segundos"""
    
    def __init__(self, ttl_segundos: int = 60):
        self.ttl = ttl_segundos
        self._cache = {}
        self._ultima_carga = 0
        self._cliente_por_usuario = {}  # Mapeo: usuario_id -> cliente_id
    
    def obtener_clientes(self) -> Dict[str, dict]:
        """Obtiene clientes del cache o recarga si expiró"""
        ahora = time.time()
        
        if ahora - self._ultima_carga > self.ttl:
            self._recargar_cache()
        
        return self._cache
    
    def _recargar_cache(self):
        """Recarga el cache desde archivos JSON y BD"""
        print("🔄 Recargando cache de clientes...")
        
        clientes = {}
        
        # 1. Cargar desde archivos JSON
        configs_dir = Path("clientes/configs")
        if configs_dir.exists():
            for config_file in configs_dir.glob("*.json"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        cliente_id = config.get('cliente_id')
                        if cliente_id:
                            clientes[cliente_id] = config
                except Exception as e:
                    print(f"⚠️ Error cargando {config_file}: {e}")
        
        # 2. También cargar desde BD (para clientes creados recientemente)
        try:
            conn = db_saas._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT cliente_id, nombre, config_json FROM clientes WHERE estado = 'activo'")
            
            for row in cursor.fetchall():
                cliente_id = row['cliente_id']
                if cliente_id not in clientes:  # Solo si no está ya cargado
                    try:
                        config = json.loads(row['config_json']) if row['config_json'] else {}
                        config['cliente_id'] = cliente_id
                        config['nombre'] = row['nombre']
                        clientes[cliente_id] = config
                    except:
                        pass
            
            conn.close()
        except Exception as e:
            print(f"⚠️ Error cargando desde BD: {e}")
        
        self._cache = clientes
        self._ultima_carga = time.time()
        print(f"✅ Cache actualizado: {len(clientes)} clientes activos")
    
    def obtener_cliente(self, cliente_id: str) -> Optional[dict]:
        """Obtiene un cliente específico del cache"""
        clientes = self.obtener_clientes()
        return clientes.get(cliente_id)
    
    def detectar_cliente_por_texto(self, texto: str) -> Optional[str]:
        """
        Detecta el cliente_id basado en el texto del mensaje.
        Busca palabras clave como 'publiya7', 'imprenta_xyz', etc.
        """
        texto_lower = texto.lower().strip()
        clientes = self.obtener_clientes()
        
        # Buscar coincidencia exacta de cliente_id
        for cliente_id in clientes.keys():
            if cliente_id.lower() in texto_lower:
                return cliente_id
        
        return None
    
    def guardar_relacion_usuario_cliente(self, usuario_id: str, cliente_id: str, 
                                         metodo_deteccion: str = 'automatico'):
        """Guarda la relación usuario -> cliente en memoria y BD"""
        self._cliente_por_usuario[usuario_id] = cliente_id
        
        # También guardar en BD para persistencia
        try:
            conn = db_saas._get_connection()
            cursor = conn.cursor()
            
            # Actualizar o insertar en estado_usuario
            cursor.execute("""
                INSERT INTO estado_usuario (cliente_id, usuario_id, datos_extra)
                VALUES (?, ?, ?)
                ON CONFLICT(cliente_id, usuario_id) DO UPDATE SET
                datos_extra = excluded.datos_extra,
                actualizado_en = CURRENT_TIMESTAMP
            """, (cliente_id, usuario_id, json.dumps({
                'cliente_asignado': True,
                'metodo_deteccion': metodo_deteccion,
                'fecha_asignacion': time.time()
            })))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error guardando relación en BD: {e}")
    
    def usuario_tiene_cliente_asignado(self, usuario_id: str) -> bool:
        """Verifica si un usuario ya tiene cliente asignado (bloqueo de cambio)"""
        cliente_id = self.obtener_cliente_de_usuario(usuario_id)
        return cliente_id is not None
    
    def log_deteccion(self, usuario_id: str, texto: str, cliente_detectado: str, 
                      metodo: str, exito: bool):
        """Guarda log de detección para análisis futuro"""
        try:
            conn = db_saas._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversaciones 
                (cliente_id, usuario_id, mensaje, tipo, paso)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cliente_detectado or 'desconocido',
                usuario_id,
                texto[:500],  # Limitar longitud
                'deteccion',
                1 if exito else 0
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Error guardando log: {e}")
    
    def obtener_cliente_de_usuario(self, usuario_id: str) -> Optional[str]:
        """Obtiene el cliente asignado a un usuario"""
        # Primero buscar en memoria
        if usuario_id in self._cliente_por_usuario:
            return self._cliente_por_usuario[usuario_id]
        
        # Si no está en memoria, buscar en BD
        try:
            conn = db_saas._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cliente_id FROM estado_usuario 
                WHERE usuario_id = ?
                ORDER BY actualizado_en DESC LIMIT 1
            """, (usuario_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                cliente_id = row['cliente_id']
                self._cliente_por_usuario[usuario_id] = cliente_id
                return cliente_id
        except Exception as e:
            print(f"⚠️ Error leyendo relación de BD: {e}")
        
        return None
    
    def forzar_recarga(self):
        """Fuerza la recarga inmediata del cache"""
        self._ultima_carga = 0
        self.obtener_clientes()

# Instancia global del cache
cliente_cache = ClienteCache(ttl_segundos=60)
