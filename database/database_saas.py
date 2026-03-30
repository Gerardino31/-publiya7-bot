"""
database_saas.py - Base de datos BotlyPro SaaS
Gestiona carritos, pedidos y productos multi-cliente
Soporta SQLite (local) y PostgreSQL (producción)
"""

import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

# Detectar si usamos PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    print(f"[DB] Usando PostgreSQL")
else:
    import sqlite3
    print("[DB] Usando SQLite")


class DatabaseSaaS:
    """Base de datos para BotlyPro SaaS"""
    
    def __init__(self, db_path: str = None):
        if USE_POSTGRES:
            self.init_postgres()
        else:
            # SQLite
            if db_path is None:
                disk_path = os.environ.get('DISK_PATH', '/data')
                self.db_path = os.path.join(disk_path, "botlypro_saas.db")
                print(f"[INFO] Usando base de datos en: {self.db_path}")
            else:
                self.db_path = db_path
            self.init_sqlite()
    
    def _get_connection(self):
        """Obtiene conexión a la base de datos"""
        if USE_POSTGRES:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        else:
            conn = sqlite3.connect(self.db_path, timeout=20.0)
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_postgres(self):
        """Inicializa tablas en PostgreSQL"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Crear todas las tablas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carritos (
                    id SERIAL PRIMARY KEY,
                    cliente_id VARCHAR(50) NOT NULL,
                    usuario_id VARCHAR(100) NOT NULL,
                    estado VARCHAR(50) DEFAULT 'activo',
                    total INTEGER DEFAULT 0,
                    cantidad_items INTEGER DEFAULT 0,
                    expira_en TIMESTAMP,
                    creado_en TIMESTAMP DEFAULT NOW()
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carrito_items (
                    id SERIAL PRIMARY KEY,
                    carrito_id INTEGER REFERENCES carritos(id) ON DELETE CASCADE,
                    producto_id VARCHAR(100),
                    nombre_producto VARCHAR(200),
                    cantidad VARCHAR(50),
                    precio_unitario INTEGER,
                    subtotal INTEGER,
                    agregado_en TIMESTAMP DEFAULT NOW()
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id SERIAL PRIMARY KEY,
                    numero_orden VARCHAR(50) UNIQUE NOT NULL,
                    cliente_id VARCHAR(50) NOT NULL,
                    usuario_id VARCHAR(100) NOT NULL,
                    carrito_id INTEGER,
                    subtotal INTEGER DEFAULT 0,
                    descuento INTEGER DEFAULT 0,
                    total INTEGER DEFAULT 0,
                    cantidad_items INTEGER,
                    estado VARCHAR(50) DEFAULT 'pendiente',
                    nombre_comprador VARCHAR(200),
                    telefono_contacto VARCHAR(50),
                    email_contacto VARCHAR(200),
                    direccion_entrega TEXT,
                    ciudad_entrega VARCHAR(100),
                    metodo_pago VARCHAR(50),
                    estado_pago VARCHAR(50) DEFAULT 'pendiente',
                    notas_cliente TEXT,
                    notas_internas TEXT,
                    creado_en TIMESTAMP DEFAULT NOW(),
                    confirmado_en TIMESTAMP,
                    pagado_en TIMESTAMP,
                    enviado_en TIMESTAMP,
                    completado_en TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedido_items (
                    id SERIAL PRIMARY KEY,
                    pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
                    producto_id VARCHAR(100),
                    nombre_producto VARCHAR(200),
                    cantidad VARCHAR(50),
                    medidas VARCHAR(50),
                    precio_unitario INTEGER,
                    subtotal INTEGER
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estado_usuario (
                    id SERIAL PRIMARY KEY,
                    cliente_id VARCHAR(50) NOT NULL,
                    usuario_id VARCHAR(100) NOT NULL,
                    paso INTEGER DEFAULT 0,
                    categoria VARCHAR(100),
                    producto INTEGER,
                    cantidad VARCHAR(50),
                    total INTEGER DEFAULT 0,
                    datos_extra TEXT,
                    carrito_id INTEGER,
                    actualizado_en TIMESTAMP DEFAULT NOW(),
                    UNIQUE(cliente_id, usuario_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversaciones (
                    id SERIAL PRIMARY KEY,
                    cliente_id VARCHAR(50),
                    user_id VARCHAR(100),
                    mensaje TEXT,
                    respuesta TEXT,
                    tipo VARCHAR(50),
                    fecha TIMESTAMP DEFAULT NOW()
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comprobantes_pago (
                    id SERIAL PRIMARY KEY,
                    cliente_id VARCHAR(50) NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    pedido_id VARCHAR(50) NOT NULL,
                    imagen_data TEXT,
                    estado VARCHAR(50) DEFAULT 'pendiente',
                    fecha_envio TIMESTAMP DEFAULT NOW(),
                    verificado_por VARCHAR(100),
                    fecha_verificacion TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS modo_usuario (
                    id SERIAL PRIMARY KEY,
                    cliente_id VARCHAR(50) NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    modo VARCHAR(50) DEFAULT 'bot',
                    activado_por VARCHAR(100) DEFAULT 'sistema',
                    fecha_cambio TIMESTAMP DEFAULT NOW(),
                    UNIQUE(cliente_id, user_id)
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Base de datos PostgreSQL inicializada")
            
        except Exception as e:
            print(f"[DB ERROR] Error inicializando PostgreSQL: {e}")
    
    def init_sqlite(self):
        """Inicializa tablas en SQLite"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Ejecutar schema desde archivo
            schema_path = Path(__file__).parent / "schema_saas_pro.sql"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = f.read()
                cursor.executescript(schema)
                conn.commit()
            
            conn.close()
            print("✅ Base de datos SQLite inicializada")
        except Exception as e:
            print(f"[DB ERROR] {e}")
    
    # ============================================
    # CARRITOS
    # ============================================
    
    def crear_carrito(self, cliente_id: str, usuario_id: str) -> int:
        """Crea un nuevo carrito"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            expira = datetime.now() + timedelta(minutes=30)
            if USE_POSTGRES:
                cursor.execute("""
                    INSERT INTO carritos (cliente_id, usuario_id, expira_en)
                    VALUES (%s, %s, %s) RETURNING id
                """, (cliente_id, usuario_id, expira))
                carrito_id = cursor.fetchone()[0]
            else:
                cursor.execute("""
                    INSERT INTO carritos (cliente_id, usuario_id, expira_en)
                    VALUES (?, ?, ?)
                """, (cliente_id, usuario_id, expira))
                carrito_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return carrito_id
        except Exception as e:
            conn.close()
            # Buscar carrito existente
            return self._buscar_carrito_existente(cliente_id, usuario_id)
    
    def _buscar_carrito_existente(self, cliente_id: str, usuario_id: str) -> Optional[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cursor.execute(f"""
            SELECT id FROM carritos 
            WHERE cliente_id = {ph} AND usuario_id = {ph} AND estado = 'activo'
            ORDER BY creado_en DESC LIMIT 1
        """, (cliente_id, usuario_id))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    
    def obtener_carrito_activo(self, cliente_id: str, usuario_id: str) -> Optional[Dict]:
        """Obtiene carrito activo o crea uno nuevo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            ph = "%s" if USE_POSTGRES else "?"
            now = datetime.now()
            
            cursor.execute(f"""
                SELECT * FROM carritos 
                WHERE cliente_id = {ph} AND usuario_id = {ph} 
                AND estado = 'activo' 
                AND (expira_en IS NULL OR expira_en > {ph})
                ORDER BY creado_en DESC LIMIT 1
            """, (cliente_id, usuario_id, now))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'cliente_id': row[1],
                    'usuario_id': row[2],
                    'estado': row[3],
                    'total': row[4] or 0,
                    'cantidad_items': row[5] or 0,
                    'expira_en': row[6],
                    'creado_en': row[7]
                }
            
            # Crear nuevo carrito
            carrito_id = self.crear_carrito(cliente_id, usuario_id)
            return self.obtener_carrito_por_id(carrito_id) if carrito_id else None
            
        except Exception as e:
            print(f"[ERROR] obtener_carrito_activo: {e}")
            return None
    
    def obtener_carrito_por_id(self, carrito_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cursor.execute(f"SELECT * FROM carritos WHERE id = {ph}", (carrito_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'cliente_id': row[1],
                'usuario_id': row[2],
                'estado': row[3],
                'total': row[4] or 0,
                'cantidad_items': row[5] or 0,
                'expira_en': row[6],
                'creado_en': row[7]
            }
        return None
    
    def agregar_item_carrito(self, carrito_id: int, producto: Dict, 
                            cantidad: int = None, medidas: str = None, area: float = None,
                            precio_unitario: int = None, subtotal: int = None) -> bool:
        """Agrega un item al carrito"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Preparar cantidad
            if medidas:
                cantidad_str = medidas
            elif cantidad:
                cantidad_str = str(cantidad)
            else:
                cantidad_str = "1"
            
            ph = "%s" if USE_POSTGRES else "?"
            cursor.execute(f"""
                INSERT INTO carrito_items (carrito_id, producto_id, nombre_producto, cantidad, precio_unitario, subtotal)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            """, (carrito_id, producto.get('prod_id') or producto.get('id'), 
                  producto.get('nombre'), cantidad_str,
                  int(precio_unitario) if precio_unitario else 0,
                  int(subtotal) if subtotal else 0))
            
            # Actualizar totales
            cursor.execute(f"""
                UPDATE carritos 
                SET total = COALESCE(total, 0) + {ph}, cantidad_items = COALESCE(cantidad_items, 0) + 1
                WHERE id = {ph}
            """, (int(subtotal) if subtotal else 0, carrito_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"[ERROR] agregar_item_carrito: {e}")
            return False
    
    def obtener_items_carrito(self, carrito_id: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cursor.execute(f"SELECT * FROM carrito_items WHERE carrito_id = {ph}", (carrito_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'producto_id': row[2],
            'nombre_producto': row[3],
            'cantidad': row[4],
            'precio_unitario': row[5],
            'subtotal': row[6]
        } for row in rows]
    
    def limpiar_carrito(self, carrito_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            cursor.execute(f"DELETE FROM carrito_items WHERE carrito_id = {ph}", (carrito_id,))
            cursor.execute(f"""
                UPDATE carritos SET total = 0, cantidad_items = 0 WHERE id = {ph}
            """, (carrito_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            return False
    
    # ============================================
    # PEDIDOS
    # ============================================
    
    def crear_pedido(self, carrito_id: int, cliente_id: str, usuario_id: str,
                     subtotal: int = None, total: int = None, cantidad_items: int = None,
                     nombre_comprador: str = None, telefono: str = None,
                     telefono_contacto: str = None, direccion: str = None) -> Optional[str]:
        """Crea un nuevo pedido"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Generar número único
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = random.randint(1000, 9999)
            numero_orden = f"ORD-{timestamp}-{random_suffix}"
            
            telefono_final = telefono_contacto if telefono_contacto else telefono
            
            ph = "%s" if USE_POSTGRES else "?"
            if USE_POSTGRES:
                cursor.execute(f"""
                    INSERT INTO pedidos (numero_orden, cliente_id, usuario_id, carrito_id, 
                        subtotal, total, cantidad_items, nombre_comprador, telefono_contacto, 
                        direccion_entrega, estado, confirmado_en)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, 'confirmado', NOW()) RETURNING id
                """, (numero_orden, cliente_id, usuario_id, carrito_id,
                      subtotal or 0, total or 0, cantidad_items or 0,
                      nombre_comprador, telefono_final, direccion))
            else:
                cursor.execute(f"""
                    INSERT INTO pedidos (numero_orden, cliente_id, usuario_id, carrito_id, 
                        subtotal, total, cantidad_items, nombre_comprador, telefono_contacto, 
                        direccion_entrega, estado, confirmado_en)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, 'confirmado', datetime('now'))
                """, (numero_orden, cliente_id, usuario_id, carrito_id,
                      subtotal or 0, total or 0, cantidad_items or 0,
                      nombre_comprador, telefono_final, direccion))
            
            # Copiar items
            items = self.obtener_items_carrito(carrito_id)
            for item in items:
                cursor.execute(f"""
                    INSERT INTO pedido_items (pedido_id, producto_id, nombre_producto, cantidad, precio_unitario, subtotal)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                """, (carrito_id, item['producto_id'], item['nombre_producto'],
                      item['cantidad'], item['precio_unitario'], item['subtotal']))
            
            self.limpiar_carrito(carrito_id)
            conn.commit()
            conn.close()
            return numero_orden
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"[ERROR] crear_pedido: {e}")
            return None
    
    def obtener_pedido(self, numero_orden: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cursor.execute(f"SELECT * FROM pedidos WHERE numero_orden = {ph}", (numero_orden,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'numero_orden': row[1],
                'cliente_id': row[2],
                'usuario_id': row[3],
                'total': row[6],
                'estado': row[10]
            }
        return None
    
    # ============================================
    # ESTADO USUARIO
    # ============================================
    
    def guardar_estado(self, cliente_id: str, user_id: str, estado: Dict) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            now = datetime.now()
            
            # Verificar si existe
            cursor.execute(f"""
                SELECT id FROM estado_usuario WHERE cliente_id = {ph} AND usuario_id = {ph}
            """, (cliente_id, user_id))
            
            if cursor.fetchone():
                # Actualizar
                if USE_POSTGRES:
                    cursor.execute(f"""
                        UPDATE estado_usuario 
                        SET paso = {ph}, categoria = {ph}, producto = {ph}, cantidad = {ph}, 
                            total = {ph}, datos_extra = {ph}, actualizado_en = NOW()
                        WHERE cliente_id = {ph} AND usuario_id = {ph}
                    """, (estado.get('paso', 0), estado.get('categoria'), estado.get('producto'),
                          str(estado.get('cantidad')) if estado.get('cantidad') else None,
                          estado.get('total', 0), json.dumps(estado.get('datos_extra', {})),
                          cliente_id, user_id))
                else:
                    cursor.execute(f"""
                        UPDATE estado_usuario 
                        SET paso = {ph}, categoria = {ph}, producto = {ph}, cantidad = {ph}, 
                            total = {ph}, datos_extra = {ph}, actualizado_en = datetime('now')
                        WHERE cliente_id = {ph} AND usuario_id = {ph}
                    """, (estado.get('paso', 0), estado.get('categoria'), estado.get('producto'),
                          str(estado.get('cantidad')) if estado.get('cantidad') else None,
                          estado.get('total', 0), json.dumps(estado.get('datos_extra', {})),
                          cliente_id, user_id))
            else:
                # Insertar
                cursor.execute(f"""
                    INSERT INTO estado_usuario (cliente_id, usuario_id, paso, categoria, producto, cantidad, total, datos_extra)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                """, (cliente_id, user_id, estado.get('paso', 0), estado.get('categoria'),
                      estado.get('producto'), str(estado.get('cantidad')) if estado.get('cantidad') else None,
                      estado.get('total', 0), json.dumps(estado.get('datos_extra', {}))))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"[ERROR] guardar_estado: {e}")
            return False
    
    def obtener_estado(self, cliente_id: str, user_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cursor.execute(f"""
            SELECT paso, categoria, producto, cantidad, total, datos_extra 
            FROM estado_usuario WHERE cliente_id = {ph} AND usuario_id = {ph}
        """, (cliente_id, user_id))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'paso': row[0],
                'categoria': row[1],
                'producto': row[2],
                'cantidad': row[3],
                'total': row[4],
                'datos_extra': json.loads(row[5]) if row[5] else {}
            }
        return None
    
    def limpiar_estado(self, cliente_id: str, user_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            cursor.execute(f"""
                DELETE FROM estado_usuario WHERE cliente_id = {ph} AND usuario_id = {ph}
            """, (cliente_id, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    # ============================================
    # CONVERSACIONES
    # ============================================
    
    def guardar_conversacion(self, cliente_id: str, user_id: str, 
                            mensaje: str, respuesta: str, tipo: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            cursor.execute(f"""
                INSERT INTO conversaciones (cliente_id, user_id, mensaje, respuesta, tipo)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            """, (cliente_id, user_id, mensaje, respuesta, tipo))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            return False
    
    # ============================================
    # COMPROBANTES PAGO
    # ============================================
    
    def guardar_comprobante_pago(self, cliente_id: str, user_id: str, 
                                  pedido_id: str, imagen_data: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            cursor.execute(f"""
                INSERT INTO comprobantes_pago (cliente_id, user_id, pedido_id, imagen_data)
                VALUES ({ph}, {ph}, {ph}, {ph}) RETURNING id
            """, (cliente_id, user_id, pedido_id, imagen_data))
            
            if USE_POSTGRES:
                comprobante_id = cursor.fetchone()[0]
            else:
                comprobante_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return comprobante_id
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"[ERROR] guardar_comprobante_pago: {e}")
            return 0
    
    def obtener_comprobantes_pendientes(self, cliente_id: str) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        ph = "%s" if USE_POSTGRES else "?"
        cursor.execute(f"""
            SELECT id, pedido_id, user_id, fecha_envio FROM comprobantes_pago 
            WHERE cliente_id = {ph} AND estado = 'pendiente'
        """, (cliente_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{'id': r[0], 'pedido_id': r[1], 'user_id': r[2], 'fecha_envio': r[3]} for r in rows]
    
    def verificar_comprobante(self, comprobante_id: int, admin: str, estado: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            if USE_POSTGRES:
                cursor.execute(f"""
                    UPDATE comprobantes_pago 
                    SET estado = {ph}, verificado_por = {ph}, fecha_verificacion = NOW()
                    WHERE id = {ph}
                """, (estado, admin, comprobante_id))
            else:
                cursor.execute(f"""
                    UPDATE comprobantes_pago 
                    SET estado = {ph}, verificado_por = {ph}, fecha_verificacion = datetime('now')
                    WHERE id = {ph}
                """, (estado, admin, comprobante_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            return False
    
    # ============================================
    # MODO USUARIO
    # ============================================
    
    def obtener_modo_usuario(self, cliente_id: str, user_id: str) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            cursor.execute(f"""
                SELECT modo FROM modo_usuario WHERE cliente_id = {ph} AND user_id = {ph}
            """, (cliente_id, user_id))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else 'bot'
        except Exception as e:
            conn.close()
            return 'bot'
    
    def set_modo_usuario(self, cliente_id: str, user_id: str, modo: str, activado_por: str = 'sistema') -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            ph = "%s" if USE_POSTGRES else "?"
            
            # Verificar si existe
            cursor.execute(f"""
                SELECT id FROM modo_usuario WHERE cliente_id = {ph} AND user_id = {ph}
            """, (cliente_id, user_id))
            
            if cursor.fetchone():
                if USE_POSTGRES:
                    cursor.execute(f"""
                        UPDATE modo_usuario 
                        SET modo = {ph}, activado_por = {ph}, fecha_cambio = NOW()
                        WHERE cliente_id = {ph} AND user_id = {ph}
                    """, (modo, activado_por, cliente_id, user_id))
                else:
                    cursor.execute(f"""
                        UPDATE modo_usuario 
                        SET modo = {ph}, activado_por = {ph}, fecha_cambio = datetime('now')
                        WHERE cliente_id = {ph} AND user_id = {ph}
                    """, (modo, activado_por, cliente_id, user_id))
            else:
                cursor.execute(f"""
                    INSERT INTO modo_usuario (cliente_id, user_id, modo, activado_por)
                    VALUES ({ph}, {ph}, {ph}, {ph})
                """, (cliente_id, user_id, modo, activado_por))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.rollback()
            conn.close()
            return False
    
    def guardar_mensaje_asesor(self, cliente_id: str, user_id: str, mensaje: str, asesor: str) -> bool:
        print(f"[MODO HUMANO] Mensaje de {asesor} para {user_id}: {mensaje[:50]}...")
        return True
    
    def obtener_mensajes_pendientes_asesor(self, cliente_id: str, user_id: str) -> List[Dict]:
        return []


# Instancia global
db_saas = DatabaseSaaS()
