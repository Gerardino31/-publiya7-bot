"""
database_saas.py - Base de datos BotlyPro SaaS
Gestiona carritos, pedidos y productos multi-cliente
"""

import sqlite3
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

class DatabaseSaaS:
    """Base de datos para BotlyPro SaaS"""
    
    def __init__(self, db_path: str = "botlypro_saas.db"):
        self.db_path = db_path
        self.init_database()
    
    def _get_connection(self):
        """Obtiene conexión a la base de datos con timeout"""
        conn = sqlite3.connect(self.db_path, timeout=20.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicializa todas las tablas"""
        schema_path = Path(__file__).parent / "schema_saas_pro.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executescript(schema)
            conn.commit()
            conn.close()
            print("✅ Base de datos SaaS inicializada")
    
    # ============================================
    # CARRITOS
    # ============================================
    
    def crear_carrito(self, cliente_id: str, usuario_id: str) -> int:
        """Crea un nuevo carrito para un usuario"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calcular expiración (30 minutos)
            expira = datetime.now() + timedelta(minutes=30)
            
            cursor.execute("""
                INSERT INTO carritos (cliente_id, usuario_id, expira_en)
                VALUES (?, ?, ?)
            """, (cliente_id, usuario_id, expira))
            
            carrito_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return carrito_id
        except sqlite3.IntegrityError:
            # El carrito ya existe, obtener el ID
            conn.close()
            carrito = self.obtener_carrito_activo(cliente_id, usuario_id)
            return carrito['id'] if carrito else None
    
    def obtener_carrito_activo(self, cliente_id: str, usuario_id: str) -> Optional[Dict]:
        """Obtiene el carrito activo de un usuario, o crea uno nuevo"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Buscar carrito activo no expirado
        cursor.execute("""
            SELECT * FROM carritos 
            WHERE cliente_id = ? AND usuario_id = ? 
            AND estado = 'activo' 
            AND (expira_en IS NULL OR expira_en > ?)
            ORDER BY creado_en DESC LIMIT 1
        """, (cliente_id, usuario_id, datetime.now()))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        
        # Si no hay carrito activo, crear uno nuevo
        carrito_id = self.crear_carrito(cliente_id, usuario_id)
        return self.obtener_carrito_por_id(carrito_id)
    
    def obtener_carrito_por_id(self, carrito_id: int) -> Optional[Dict]:
        """Obtiene un carrito por su ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM carritos WHERE id = ?", (carrito_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def agregar_item_carrito(self, carrito_id: int, producto: Dict, 
                            cantidad: int = None, medidas: str = None, 
                            area: int = None, precio_unitario: int = None) -> bool:
        """Agrega un item al carrito"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Calcular subtotal
        if cantidad and precio_unitario:
            subtotal = cantidad * precio_unitario
        elif area and precio_unitario:
            subtotal = int(area * precio_unitario)
        else:
            subtotal = 0
        
        cursor.execute("""
            INSERT INTO carrito_items 
            (carrito_id, producto_id, categoria_id, prod_id, nombre_producto,
             cantidad, medidas, area, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            carrito_id,
            producto.get('id'),
            producto.get('categoria_id'),
            producto.get('prod_id'),
            producto.get('nombre'),
            cantidad,
            medidas,
            area,
            precio_unitario,
            subtotal
        ))
        
        # Actualizar totales del carrito
        self._actualizar_totales_carrito(carrito_id, conn)
        
        conn.commit()
        conn.close()
        
        return True
    
    def _actualizar_totales_carrito(self, carrito_id: int, conn):
        """Actualiza los totales del carrito"""
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as items, SUM(subtotal) as total 
            FROM carrito_items 
            WHERE carrito_id = ?
        """, (carrito_id,))
        
        row = cursor.fetchone()
        cantidad_items = row['items'] or 0
        total = row['total'] or 0
        
        cursor.execute("""
            UPDATE carritos 
            SET cantidad_items = ?, total = ?, actualizado_en = ?
            WHERE id = ?
        """, (cantidad_items, total, datetime.now(), carrito_id))
    
    def obtener_items_carrito(self, carrito_id: int) -> List[Dict]:
        """Obtiene todos los items de un carrito"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM carrito_items 
            WHERE carrito_id = ?
            ORDER BY agregado_en DESC
        """, (carrito_id,))
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return items
    
    def limpiar_carrito(self, carrito_id: int) -> bool:
        """Limpia todos los items de un carrito"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM carrito_items WHERE carrito_id = ?", (carrito_id,))
        
        # Resetear totales
        cursor.execute("""
            UPDATE carritos 
            SET cantidad_items = 0, total = 0, actualizado_en = ?
            WHERE id = ?
        """, (datetime.now(), carrito_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    # ============================================
    # PEDIDOS
    # ============================================
    
    def crear_pedido(self, carrito_id: int, cliente_id: str, usuario_id: str,
                     nombre_comprador: str = None, telefono_contacto: str = None,
                     direccion_entrega: str = None) -> Optional[str]:
        """Convierte un carrito en pedido"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Obtener items del carrito
        items = self.obtener_items_carrito(carrito_id)
        if not items:
            conn.close()
            return None
        
        # Calcular totales
        total = sum(item['subtotal'] for item in items)
        cantidad_items = len(items)
        
        # Generar número de orden
        numero_orden = f"ORD-{datetime.now().strftime('%Y%m%d')}-{carrito_id:04d}"
        
        # Crear pedido
        cursor.execute("""
            INSERT INTO pedidos 
            (numero_orden, cliente_id, usuario_id, carrito_id, subtotal, total,
             cantidad_items, nombre_comprador, telefono_contacto, direccion_entrega,
             estado, confirmado_en)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmado', ?)
        """, (numero_orden, cliente_id, usuario_id, carrito_id, total, total,
              cantidad_items, nombre_comprador, telefono_contacto, direccion_entrega,
              datetime.now()))
        
        pedido_id = cursor.lastrowid
        
        # Copiar items al pedido
        for item in items:
            cursor.execute("""
                INSERT INTO pedido_items
                (pedido_id, producto_id, categoria_id, prod_id, nombre_producto,
                 cantidad, medidas, area, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pedido_id, item['producto_id'], item['categoria_id'], 
                  item['prod_id'], item['nombre_producto'], item['cantidad'],
                  item['medidas'], item['area'], item['precio_unitario'], 
                  item['subtotal']))
        
        # Marcar carrito como completado
        cursor.execute("""
            UPDATE carritos 
            SET estado = 'completado', actualizado_en = ?
            WHERE id = ?
        """, (datetime.now(), carrito_id))
        
        conn.commit()
        conn.close()
        
        return numero_orden
    
    def obtener_pedido(self, numero_orden: str) -> Optional[Dict]:
        """Obtiene un pedido por su número"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pedidos WHERE numero_orden = ?", (numero_orden,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # ============================================
    # PRODUCTOS
    # ============================================
    
    def obtener_producto(self, cliente_id: str, categoria_id: str, prod_id: str) -> Optional[Dict]:
        """Obtiene un producto específico"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM productos 
            WHERE cliente_id = ? AND categoria_id = ? AND prod_id = ? AND activo = 1
        """, (cliente_id, categoria_id, prod_id))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def listar_productos_categoria(self, cliente_id: str, categoria_id: str) -> List[Dict]:
        """Lista todos los productos de una categoría"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM productos 
            WHERE cliente_id = ? AND categoria_id = ? AND activo = 1
            ORDER BY orden, nombre
        """, (cliente_id, categoria_id))
        
        productos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return productos
    
    # ============================================
    # ESTADO DE CONVERSACIÓN (migrado desde db.py)
    # ============================================
    
    def guardar_estado(self, cliente_id: str, user_id: str, estado: Dict) -> bool:
        """Guarda el estado de una conversación"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Crear tabla si no existe
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
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cliente_id, user_id)
                )
            ''')
            
            # Convertir datos extra a JSON
            datos_extra = json.dumps(estado.get('datos_extra', {}))
            cantidad = estado.get('cantidad')
            if cantidad is not None:
                cantidad = str(cantidad)
            
            cursor.execute('''
                INSERT OR REPLACE INTO estado_conversacion 
                (cliente_id, user_id, paso, categoria, producto, cantidad, total, datos_extra, actualizado_en)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cliente_id,
                user_id,
                estado.get('paso', 0),
                estado.get('categoria'),
                estado.get('producto'),
                cantidad,
                estado.get('total', 0),
                datos_extra,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"[WARNING] Base de datos bloqueada, reintentando...")
                import time
                time.sleep(0.1)
                return self.guardar_estado(cliente_id, user_id, estado)
            print(f"[ERROR] guardar_estado: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] guardar_estado: {e}")
            return False
    
    def obtener_estado(self, cliente_id: str, user_id: str) -> Optional[Dict]:
        """Obtiene el estado de una conversación"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Crear tabla si no existe
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
                    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cliente_id, user_id)
                )
            ''')
            conn.commit()
            
            cursor.execute('''
                SELECT * FROM estado_conversacion 
                WHERE cliente_id = ? AND user_id = ?
            ''', (cliente_id, user_id))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                estado = dict(row)
                # Parsear cantidad
                try:
                    estado['cantidad'] = int(estado['cantidad'])
                except (ValueError, TypeError):
                    pass
                # Parsear datos extra
                if estado.get('datos_extra'):
                    try:
                        estado['datos_extra'] = json.loads(estado['datos_extra'])
                    except:
                        estado['datos_extra'] = {}
                return estado
            return None
        except Exception as e:
            print(f"[ERROR] obtener_estado: {e}")
            return None
    
    def limpiar_estado(self, cliente_id: str, user_id: str) -> bool:
        """Limpia el estado de una conversación"""
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
            print(f"[ERROR] limpiar_estado: {e}")
            return False
    
    def guardar_conversacion(self, cliente_id: str, user_id: str, mensaje: str, respuesta: str, tipo: str) -> bool:
        """Guarda un mensaje de conversación para auditoría"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verificar si tabla existe y tiene la columna user_id
            cursor.execute("PRAGMA table_info(conversaciones)")
            columnas = cursor.fetchall()
            
            if not columnas:
                # Tabla no existe, crearla
                cursor.execute('''
                    CREATE TABLE conversaciones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_id TEXT,
                        user_id TEXT,
                        mensaje TEXT,
                        respuesta TEXT,
                        tipo TEXT,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            else:
                # Tabla existe, verificar si tiene user_id
                nombres_columnas = [col[1] for col in columnas]
                if 'user_id' not in nombres_columnas:
                    # Backup de datos, recrear tabla
                    cursor.execute('ALTER TABLE conversaciones RENAME TO conversaciones_old')
                    cursor.execute('''
                        CREATE TABLE conversaciones (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cliente_id TEXT,
                            user_id TEXT,
                            mensaje TEXT,
                            respuesta TEXT,
                            tipo TEXT,
                            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    cursor.execute('DROP TABLE conversaciones_old')
            
            cursor.execute('''
                INSERT INTO conversaciones (cliente_id, user_id, mensaje, respuesta, tipo)
                VALUES (?, ?, ?, ?, ?)
            ''', (cliente_id, user_id, mensaje, respuesta, tipo))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"[WARNING] Base de datos bloqueada, reintentando...")
                import time
                time.sleep(0.1)
                return self.guardar_conversacion(cliente_id, user_id, mensaje, respuesta, tipo)
            print(f"[ERROR] guardar_conversacion: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] guardar_conversacion: {e}")
            return False
    
    # ============================================
    # MODO HUMANO (v2 - Asesor)
    # ============================================
    
    def obtener_modo_usuario(self, cliente_id: str, user_id: str) -> str:
        """Obtiene el modo actual del usuario (bot o humano)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuario_modo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    modo TEXT DEFAULT 'bot',
                    activado_por TEXT,
                    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cliente_id, user_id)
                )
            ''')
            
            cursor.execute('''
                SELECT modo FROM usuario_modo 
                WHERE cliente_id = ? AND user_id = ?
            ''', (cliente_id, user_id))
            
            row = cursor.fetchone()
            conn.close()
            
            return row['modo'] if row else 'bot'
        except Exception as e:
            print(f"[ERROR] obtener_modo_usuario: {e}")
            return 'bot'
    
    def set_modo_usuario(self, cliente_id: str, user_id: str, modo: str, activado_por: str = 'sistema') -> bool:
        """Cambia el modo del usuario (bot o humano)"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuario_modo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    modo TEXT DEFAULT 'bot',
                    activado_por TEXT,
                    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(cliente_id, user_id)
                )
            ''')
            
            cursor.execute('''
                INSERT OR REPLACE INTO usuario_modo 
                (cliente_id, user_id, modo, activado_por, fecha_cambio)
                VALUES (?, ?, ?, ?, ?)
            ''', (cliente_id, user_id, modo, activado_por, datetime.now()))
            
            conn.commit()
            conn.close()
            print(f"✅ Modo cambiado a '{modo}' para {user_id}")
            return True
        except Exception as e:
            print(f"[ERROR] set_modo_usuario: {e}")
            return False
    
    def guardar_mensaje_asesor(self, cliente_id: str, user_id: str, mensaje: str, asesor: str) -> bool:
        """Guarda mensaje enviado por asesor"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Crear tabla
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensajes_asesor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    mensaje TEXT,
                    asesor TEXT,
                    enviado BOOLEAN DEFAULT 0,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT INTO mensajes_asesor (cliente_id, user_id, mensaje, asesor)
                VALUES (?, ?, ?, ?)
            ''', (cliente_id, user_id, mensaje, asesor))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] guardar_mensaje_asesor: {e}")
            return False
    
    def obtener_mensajes_pendientes_asesor(self, cliente_id: str, user_id: str) -> List[Dict]:
        """Obtiene mensajes del asesor pendientes de enviar"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM mensajes_asesor 
                WHERE cliente_id = ? AND user_id = ? AND enviado = 0
                ORDER BY fecha ASC
            ''', (cliente_id, user_id))
            
            mensajes = [dict(row) for row in cursor.fetchall()]
            
            # Marcar como enviados
            cursor.execute('''
                UPDATE mensajes_asesor SET enviado = 1
                WHERE cliente_id = ? AND user_id = ? AND enviado = 0
            ''', (cliente_id, user_id))
            
            conn.commit()
            conn.close()
            return mensajes
        except Exception as e:
            print(f"[ERROR] obtener_mensajes_pendientes_asesor: {e}")
            return []

# Instancia global
db_saas = DatabaseSaaS()
