"""
database/db.py - Gestión de base de datos multi-cliente
Tablas: clientes, pedidos, conversaciones, leads
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os


class DatabaseManager:
    """Gestiona la base de datos SQLite para múltiples clientes."""
    
    def __init__(self, db_path: str = "database/pedidos.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Inicializa las tablas de la base de datos."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabla de clientes (imprentas)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                codigo_acceso TEXT UNIQUE,
                telefono TEXT,
                email TEXT,
                ciudad TEXT,
                identificador TEXT,  -- Numero WhatsApp o token del bot
                canal TEXT DEFAULT 'whatsapp',  -- whatsapp, telegram, web
                activo BOOLEAN DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_orden TEXT UNIQUE NOT NULL,
                cliente_id TEXT NOT NULL,
                user_id TEXT,
                producto TEXT NOT NULL,
                tipo TEXT,
                cantidad TEXT NOT NULL,
                precio_total INTEGER NOT NULL,
                estado TEXT DEFAULT 'nuevo',
                notas TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
            )
        ''')
        
        # Verificar si la columna user_id existe, si no, agregarla
        cursor.execute("PRAGMA table_info(pedidos)")
        columnas = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columnas:
            cursor.execute('ALTER TABLE pedidos ADD COLUMN user_id TEXT')
            print("[INFO] Columna user_id agregada a tabla pedidos")
        
        # Tabla de conversaciones (historial de chat)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                tipo_mensaje TEXT DEFAULT 'texto',
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
            )
        ''')
        
        # Tabla de leads (potenciales clientes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT NOT NULL,
                user_id TEXT,
                nombre TEXT,
                telefono TEXT,
                email TEXT,
                servicio_interes TEXT,
                estado TEXT DEFAULT 'nuevo',
                notas TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
            )
        ''')
        
        # Tabla de estado de conversacion (persistencia)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estado_conversacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                paso INTEGER DEFAULT 0,
                categoria TEXT,
                producto INTEGER,
                cantidad TEXT,
                total INTEGER DEFAULT 0,
                datos_extra TEXT,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cliente_id, user_id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[OK] Base de datos inicializada correctamente")
    
    # ========== MÉTODOS PARA CLIENTES ==========
    
    def registrar_cliente(self, cliente_id: str, nombre: str, 
                         telefono: str = None, email: str = None,
                         ciudad: str = None, codigo_acceso: str = None,
                         identificador: str = None, canal: str = 'whatsapp') -> bool:
        """Registra un nuevo cliente (imprenta)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO clientes 
                (cliente_id, nombre, telefono, email, ciudad, codigo_acceso, identificador, canal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cliente_id, nombre, telefono, email, ciudad, codigo_acceso, identificador, canal))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Error registrando cliente: {e}")
            return False
    
    def get_cliente(self, cliente_id: str) -> Optional[Dict]:
        """Obtiene información de un cliente."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM clientes WHERE cliente_id = ?",
            (cliente_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def obtener_cliente_por_identificador(self, identificador: str, canal: str = 'whatsapp') -> Optional[Dict]:
        """
        Obtiene cliente por su identificador (numero WhatsApp, token, etc.)
        Usado para deteccion automatica de clientes.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM clientes 
                WHERE identificador = ? AND canal = ? AND activo = 1
            ''', (identificador, canal))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"[ERROR] Error buscando cliente por identificador: {e}")
            return None
    
    def obtener_cliente_por_codigo(self, codigo_acceso: str) -> Optional[Dict]:
        """
        Obtiene cliente por su codigo de acceso.
        Usado para autenticacion manual.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM clientes 
                WHERE codigo_acceso = ? AND activo = 1
            ''', (codigo_acceso,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"[ERROR] Error buscando cliente por codigo: {e}")
            return None
    
    # ========== MÉTODOS PARA PEDIDOS ==========
    
    def generar_numero_orden(self) -> str:
        """Genera número de orden único."""
        fecha = datetime.now().strftime('%Y%m%d')
        random_suffix = os.urandom(2).hex().upper()
        return f"ORD-{fecha}-{random_suffix}"
    
    def guardar_pedido(self, cliente_id: str, user_id: str,
                      producto: str, tipo: str, cantidad: str,
                      precio_total: int, notas: str = "", numero_orden: str = None) -> Optional[str]:
        """Guarda un nuevo pedido en la base de datos."""
        try:
            # Usar numero_orden proporcionado o generar uno nuevo
            if numero_orden is None:
                numero_orden = self.generar_numero_orden()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pedidos 
                (numero_orden, cliente_id, user_id, producto, tipo, 
                 cantidad, precio_total, estado, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'nuevo', ?)
            ''', (numero_orden, cliente_id, user_id, producto, tipo,
                  cantidad, precio_total, notas))
            
            conn.commit()
            conn.close()
            
            print(f"[OK] Pedido guardado: {numero_orden}")
            return numero_orden
            
        except Exception as e:
            print(f"[ERROR] Error guardando pedido: {e}")
            return None
    
    def get_pedido(self, numero_orden: str) -> Optional[Dict]:
        """Obtiene un pedido por su número."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM pedidos WHERE numero_orden = ?",
            (numero_orden,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def listar_pedidos(self, cliente_id: str = None, 
                      estado: str = None, limite: int = 50) -> List[Dict]:
        """Lista pedidos con filtros opcionales."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM pedidos WHERE 1=1"
        params = []
        
        if cliente_id:
            query += " AND cliente_id = ?"
            params.append(cliente_id)
        
        if estado:
            query += " AND estado = ?"
            params.append(estado)
        
        query += " ORDER BY fecha_creacion DESC LIMIT ?"
        params.append(limite)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def actualizar_estado_pedido(self, numero_orden: str, 
                                  nuevo_estado: str) -> bool:
        """Actualiza el estado de un pedido."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE pedidos 
                SET estado = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE numero_orden = ?
            ''', (nuevo_estado, numero_orden))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Error actualizando pedido: {e}")
            return False
    
    # ========== MÉTODOS PARA CONVERSACIONES ==========
    
    def guardar_conversacion(self, cliente_id: str, user_id: str,
                            mensaje: str, respuesta: str,
                            tipo: str = 'texto') -> bool:
        """Guarda un intercambio de mensajes."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversaciones 
                (cliente_id, user_id, mensaje, respuesta, tipo_mensaje)
                VALUES (?, ?, ?, ?, ?)
            ''', (cliente_id, user_id, mensaje, respuesta, tipo))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Error guardando conversacion: {e}")
            return False
    
    def get_historial(self, cliente_id: str, user_id: str,
                     limite: int = 20) -> List[Dict]:
        """Obtiene historial de conversación."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversaciones 
            WHERE cliente_id = ? AND user_id = ?
            ORDER BY fecha DESC
            LIMIT ?
        ''', (cliente_id, user_id, limite))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== ESTADÍSTICAS ==========
    
    def get_estadisticas(self, cliente_id: str = None) -> Dict:
        """Obtiene estadísticas de pedidos."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total pedidos
        if cliente_id:
            cursor.execute(
                "SELECT COUNT(*) FROM pedidos WHERE cliente_id = ?",
                (cliente_id,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM pedidos")
        
        stats['total_pedidos'] = cursor.fetchone()[0]
        
        # Pedidos por estado
        if cliente_id:
            cursor.execute('''
                SELECT estado, COUNT(*) 
                FROM pedidos 
                WHERE cliente_id = ?
                GROUP BY estado
            ''', (cliente_id,))
        else:
            cursor.execute('''
                SELECT estado, COUNT(*) 
                FROM pedidos 
                GROUP BY estado
            ''')
        
        stats['por_estado'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return stats
    
    # ========== ESTADO DE CONVERSACIÓN (PERSISTENCIA) ==========
    
    def guardar_estado(self, cliente_id: str, user_id: str, estado: Dict) -> bool:
        """
        Guarda el estado de una conversación.
        Permite que el bot recuerde donde quedó el usuario.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convertir datos extra a JSON si existen
            datos_extra = json.dumps(estado.get('datos_extra', {}))
            
            cursor.execute('''
                INSERT INTO estado_conversacion 
                (cliente_id, user_id, paso, categoria, producto, cantidad, total, datos_extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cliente_id, user_id) 
                DO UPDATE SET
                    paso = excluded.paso,
                    categoria = excluded.categoria,
                    producto = excluded.producto,
                    cantidad = excluded.cantidad,
                    total = excluded.total,
                    datos_extra = excluded.datos_extra,
                    fecha_actualizacion = CURRENT_TIMESTAMP
            ''', (
                cliente_id,
                user_id,
                estado.get('paso', 0),
                estado.get('categoria'),
                estado.get('producto'),
                str(estado.get('cantidad', '')),
                estado.get('total', 0),
                datos_extra
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] Error guardando estado: {e}")
            return False
    
    def obtener_estado(self, cliente_id: str, user_id: str) -> Optional[Dict]:
        """
        Recupera el estado de una conversación.
        Retorna None si no hay estado guardado.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM estado_conversacion 
                WHERE cliente_id = ? AND user_id = ?
            ''', (cliente_id, user_id))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                estado = dict(row)
                # Convertir cantidad de vuelta a int si es numérica
                try:
                    estado['cantidad'] = int(estado['cantidad'])
                except (ValueError, TypeError):
                    pass  # Mantener como string si no es numérico
                
                # Parsear datos extra JSON
                if estado.get('datos_extra'):
                    try:
                        estado['datos_extra'] = json.loads(estado['datos_extra'])
                    except:
                        estado['datos_extra'] = {}
                
                return estado
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Error obteniendo estado: {e}")
            return None
    
    def limpiar_estado(self, cliente_id: str, user_id: str) -> bool:
        """
        Limpia el estado de una conversación.
        Se usa cuando el pedido se completa o se cancela.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM estado_conversacion 
                WHERE cliente_id = ? AND user_id = ?
            ''', (cliente_id, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] Error limpiando estado: {e}")
            return False
    
    def listar_conversaciones_activas(self, cliente_id: str = None) -> List[Dict]:
        """
        Lista conversaciones activas (estado paso > 0).
        Útil para ver usuarios en medio de un pedido.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if cliente_id:
                cursor.execute('''
                    SELECT * FROM estado_conversacion 
                    WHERE cliente_id = ? AND paso > 0
                    ORDER BY fecha_actualizacion DESC
                ''', (cliente_id,))
            else:
                cursor.execute('''
                    SELECT * FROM estado_conversacion 
                    WHERE paso > 0
                    ORDER BY fecha_actualizacion DESC
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"[ERROR] Error listando conversaciones: {e}")
            return []


# Instancia global
db = DatabaseManager()


# Prueba
if __name__ == "__main__":
    print("🧪 Probando base de datos...\n")
    
    # Registrar cliente de prueba
    db.registrar_cliente(
        'publiya7',
        'Publiya7 - Publicidad al Instante',
        '+57 314 390 9874',
        'publiya7@gmail.com',
        'Medellín'
    )
    
    # Guardar pedido de prueba
    orden = db.guardar_pedido(
        'publiya7',
        'user123',
        'Tarjetas de Presentación',
        'Mate 2 caras',
        '5000',
        650000,
        'Pedido de prueba'
    )
    
    if orden:
        print(f"\n📦 Pedido creado: {orden}")
        
        # Recuperar pedido
        pedido = db.get_pedido(orden)
        print(f"✅ Pedido recuperado: {pedido['producto']}")
    
    # Estadísticas
    stats = db.get_estadisticas('publiya7')
    print(f"\n📊 Estadísticas: {stats}")
