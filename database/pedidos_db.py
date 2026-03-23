# Base de datos para pedidos de Publiya7
import sqlite3
import json
from datetime import datetime
import os

class PedidosDB:
    def __init__(self, db_path='database/pedidos.db'):
        self.db_path = db_path
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializa la base de datos con las tablas necesarias."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_orden TEXT UNIQUE NOT NULL,
                cliente_id TEXT NOT NULL,
                producto TEXT NOT NULL,
                tipo TEXT,
                cantidad TEXT NOT NULL,
                precio_total INTEGER NOT NULL,
                estado TEXT DEFAULT 'nuevo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notas TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generar_numero_orden(self) -> str:
        """Genera un número de orden único."""
        fecha = datetime.now().strftime('%Y%m%d')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contar pedidos del día
        cursor.execute(
            "SELECT COUNT(*) FROM pedidos WHERE numero_orden LIKE ?",
            (f"ORD-{fecha}-%",)
        )
        count = cursor.fetchone()[0] + 1
        
        conn.close()
        
        return f"ORD-{fecha}-{count:04d}"
    
    def guardar_pedido(self, cliente_id: str, producto: str, tipo: str, 
                      cantidad: str, precio_total: int, notas: str = "") -> str:
        """Guarda un nuevo pedido en la base de datos."""
        numero_orden = self.generar_numero_orden()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pedidos (numero_orden, cliente_id, producto, tipo, 
                               cantidad, precio_total, estado, notas)
            VALUES (?, ?, ?, ?, ?, ?, 'nuevo', ?)
        ''', (numero_orden, cliente_id, producto, tipo, cantidad, precio_total, notas))
        
        conn.commit()
        conn.close()
        
        return numero_orden
    
    def obtener_pedido(self, numero_orden: str) -> dict:
        """Obtiene un pedido por su número de orden."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM pedidos WHERE numero_orden = ?",
            (numero_orden,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'numero_orden': row[1],
                'cliente_id': row[2],
                'producto': row[3],
                'tipo': row[4],
                'cantidad': row[5],
                'precio_total': row[6],
                'estado': row[7],
                'fecha_creacion': row[8],
                'fecha_actualizacion': row[9],
                'notas': row[10]
            }
        return None
    
    def listar_pedidos(self, estado=None, limite=50) -> list:
        """Lista los pedidos, opcionalmente filtrados por estado."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if estado:
            cursor.execute(
                "SELECT * FROM pedidos WHERE estado = ? ORDER BY fecha_creacion DESC LIMIT ?",
                (estado, limite)
            )
        else:
            cursor.execute(
                "SELECT * FROM pedidos ORDER BY fecha_creacion DESC LIMIT ?",
                (limite,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        pedidos = []
        for row in rows:
            pedidos.append({
                'id': row[0],
                'numero_orden': row[1],
                'cliente_id': row[2],
                'producto': row[3],
                'tipo': row[4],
                'cantidad': row[5],
                'precio_total': row[6],
                'estado': row[7],
                'fecha_creacion': row[8]
            })
        
        return pedidos
    
    def actualizar_estado(self, numero_orden: str, nuevo_estado: str):
        """Actualiza el estado de un pedido."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE pedidos 
            SET estado = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE numero_orden = ?
        ''', (nuevo_estado, numero_orden))
        
        conn.commit()
        conn.close()


# Prueba
if __name__ == "__main__":
    db = PedidosDB()
    
    # Guardar pedido de prueba
    orden = db.guardar_pedido(
        cliente_id="publiya7",
        producto="Tarjetas de Presentación",
        tipo="Mate 2 caras",
        cantidad="5000",
        precio_total=650000,
        notas="Cliente solicita diseño profesional"
    )
    
    print(f"Pedido guardado: {orden}")
    
    # Recuperar pedido
    pedido = db.obtener_pedido(orden)
    print(f"\nDetalles del pedido:")
    print(json.dumps(pedido, indent=2, default=str))
    
    # Listar pedidos
    pedidos = db.listar_pedidos()
    print(f"\nTotal pedidos: {len(pedidos)}")
