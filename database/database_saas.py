"""
database_saas.py - Base de datos BotlyPro SaaS con SQLAlchemy
Soporta SQLite (local) y PostgreSQL (producción) automáticamente
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import NullPool

# Detectar tipo de base de datos
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Producción: PostgreSQL
    print(f"[DB] Usando PostgreSQL")
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
else:
    # Desarrollo: SQLite
    disk_path = os.environ.get('DISK_PATH', '/data')
    db_path = os.path.join(disk_path, "botlypro_saas.db")
    print(f"[DB] Usando SQLite: {db_path}")
    engine = create_engine(f"sqlite:///{db_path}")

Base = declarative_base()
Session = sessionmaker(bind=engine)

# ============================================
# MODELOS
# ============================================

class Cliente(Base):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    eslogan = Column(Text)
    nit = Column(String(50))
    telefono = Column(String(50), nullable=False)
    whatsapp = Column(String(50))
    email = Column(String(200))
    direccion = Column(Text)
    ciudad = Column(String(100))
    departamento = Column(String(100))
    pais = Column(String(50), default='Colombia')
    config_json = Column(Text)
    estado = Column(String(50), default='activo')
    plan = Column(String(50), default='basico')
    fecha_registro = Column(DateTime, default=datetime.now)
    fecha_ultima_actividad = Column(DateTime)
    fecha_expiracion = Column(DateTime)
    notificar_whatsapp = Column(Boolean, default=True)
    notificar_email = Column(Boolean, default=False)
    email_notificaciones = Column(String(200))
    telefono_notificaciones = Column(String(50))
    etiquetas = Column(Text)
    notas = Column(Text)
    limite_mensajes_mes = Column(Integer, default=1000)
    limite_productos = Column(Integer, default=50)
    limite_pedidos_mes = Column(Integer, default=100)

class Carrito(Base):
    __tablename__ = 'carritos'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(String(50), nullable=False)
    usuario_id = Column(String(100), nullable=False)
    estado = Column(String(50), default='activo')
    total = Column(Integer, default=0)
    cantidad_items = Column(Integer, default=0)
    expira_en = Column(DateTime)
    creado_en = Column(DateTime, default=datetime.now)
    
    items = relationship("CarritoItem", back_populates="carrito", cascade="all, delete-orphan")

class CarritoItem(Base):
    __tablename__ = 'carrito_items'
    
    id = Column(Integer, primary_key=True)
    carrito_id = Column(Integer, ForeignKey('carritos.id', ondelete='CASCADE'))
    producto_id = Column(String(100))
    nombre_producto = Column(String(200))
    cantidad = Column(String(50))
    precio_unitario = Column(Integer)
    subtotal = Column(Integer)
    agregado_en = Column(DateTime, default=datetime.now)
    
    carrito = relationship("Carrito", back_populates="items")

class Pedido(Base):
    __tablename__ = 'pedidos'
    
    id = Column(Integer, primary_key=True)
    numero_orden = Column(String(50), unique=True, nullable=False)
    cliente_id = Column(String(50), nullable=False)
    usuario_id = Column(String(100), nullable=False)
    carrito_id = Column(Integer)
    subtotal = Column(Integer, nullable=False)
    descuento = Column(Integer, default=0)
    total = Column(Integer, nullable=False)
    cantidad_items = Column(Integer)
    estado = Column(String(50), default='pendiente')
    nombre_comprador = Column(String(200))
    telefono_contacto = Column(String(50))
    email_contacto = Column(String(200))
    direccion_entrega = Column(Text)
    ciudad_entrega = Column(String(100))
    metodo_pago = Column(String(50))
    estado_pago = Column(String(50), default='pendiente')
    notas_cliente = Column(Text)
    notas_internas = Column(Text)
    creado_en = Column(DateTime, default=datetime.now)
    confirmado_en = Column(DateTime)
    pagado_en = Column(DateTime)
    enviado_en = Column(DateTime)
    completado_en = Column(DateTime)
    
    items = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")

class PedidoItem(Base):
    __tablename__ = 'pedido_items'
    
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id', ondelete='CASCADE'))
    producto_id = Column(String(100))
    nombre_producto = Column(String(200))
    cantidad = Column(String(50))
    medidas = Column(String(50))
    precio_unitario = Column(Integer)
    subtotal = Column(Integer)
    
    pedido = relationship("Pedido", back_populates="items")

class EstadoUsuario(Base):
    __tablename__ = 'estado_usuario'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(String(50), nullable=False)
    usuario_id = Column(String(100), nullable=False)
    paso = Column(Integer, default=0)
    categoria = Column(String(100))
    producto = Column(Integer)
    cantidad = Column(String(50))
    total = Column(Integer, default=0)
    datos_extra = Column(Text)
    carrito_id = Column(Integer)
    actualizado_en = Column(DateTime, default=datetime.now)
    
    __table_args__ = (UniqueConstraint('cliente_id', 'usuario_id'),)

class Conversacion(Base):
    __tablename__ = 'conversaciones'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(String(50))
    user_id = Column(String(100))
    mensaje = Column(Text)
    respuesta = Column(Text)
    tipo = Column(String(50))
    fecha = Column(DateTime, default=datetime.now)

class ComprobantePago(Base):
    __tablename__ = 'comprobantes_pago'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(String(50), nullable=False)
    user_id = Column(String(100), nullable=False)
    pedido_id = Column(String(50), nullable=False)
    imagen_data = Column(Text)
    estado = Column(String(50), default='pendiente')
    fecha_envio = Column(DateTime, default=datetime.now)
    verificado_por = Column(String(100))
    fecha_verificacion = Column(DateTime)

class ModoUsuario(Base):
    __tablename__ = 'modo_usuario'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(String(50), nullable=False)
    user_id = Column(String(100), nullable=False)
    modo = Column(String(50), default='bot')  # 'bot' o 'humano'
    activado_por = Column(String(100), default='sistema')
    fecha_cambio = Column(DateTime, default=datetime.now)
    
    __table_args__ = (UniqueConstraint('cliente_id', 'user_id'),)

# ============================================
# INICIALIZACIÓN
# ============================================

print("[DB] Creando tablas...")
Base.metadata.create_all(engine)
print("✅ Base de datos inicializada")

# ============================================
# CLASE DATABASE SaaS
# ============================================

class DatabaseSaaS:
    """Base de datos para BotlyPro SaaS"""
    
    def __init__(self):
        self.session = Session()
    
    def _get_session(self):
        """Obtiene una nueva sesión"""
        return Session()
    
    # ============================================
    # CARRITOS
    # ============================================
    
    def crear_carrito(self, cliente_id: str, usuario_id: str) -> int:
        """Crea un nuevo carrito para un usuario"""
        session = self._get_session()
        try:
            carrito = Carrito(
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                expira_en=datetime.now() + timedelta(minutes=30)
            )
            session.add(carrito)
            session.commit()
            carrito_id = carrito.id
            session.close()
            return carrito_id
        except Exception as e:
            session.rollback()
            session.close()
            # Si ya existe, buscarlo
            return self._buscar_carrito_existente(cliente_id, usuario_id)
    
    def _buscar_carrito_existente(self, cliente_id: str, usuario_id: str) -> Optional[int]:
        """Busca un carrito existente"""
        session = self._get_session()
        carrito = session.query(Carrito).filter(
            Carrito.cliente_id == cliente_id,
            Carrito.usuario_id == usuario_id,
            Carrito.estado == 'activo'
        ).order_by(Carrito.creado_en.desc()).first()
        session.close()
        return carrito.id if carrito else None
    
    def obtener_carrito_activo(self, cliente_id: str, usuario_id: str) -> Optional[Dict]:
        """Obtiene el carrito activo de un usuario, o crea uno nuevo"""
        session = self._get_session()
        try:
            carrito = session.query(Carrito).filter(
                Carrito.cliente_id == cliente_id,
                Carrito.usuario_id == usuario_id,
                Carrito.estado == 'activo'
            ).order_by(Carrito.creado_en.desc()).first()
            
            if carrito and (carrito.expira_en is None or carrito.expira_en > datetime.now()):
                result = {
                    'id': carrito.id,
                    'cliente_id': carrito.cliente_id,
                    'usuario_id': carrito.usuario_id,
                    'estado': carrito.estado,
                    'total': carrito.total,
                    'cantidad_items': carrito.cantidad_items,
                    'expira_en': carrito.expira_en,
                    'creado_en': carrito.creado_en
                }
                session.close()
                return result
            
            session.close()
            
            # Si no hay carrito activo, crear uno nuevo
            carrito_id = self.crear_carrito(cliente_id, usuario_id)
            return self.obtener_carrito_por_id(carrito_id) if carrito_id else None
            
        except Exception as e:
            session.close()
            print(f"[ERROR] obtener_carrito_activo: {e}")
            return None
    
    def obtener_carrito_por_id(self, carrito_id: int) -> Optional[Dict]:
        """Obtiene un carrito por su ID"""
        session = self._get_session()
        carrito = session.query(Carrito).filter(Carrito.id == carrito_id).first()
        session.close()
        
        if carrito:
            return {
                'id': carrito.id,
                'cliente_id': carrito.cliente_id,
                'usuario_id': carrito.usuario_id,
                'estado': carrito.estado,
                'total': carrito.total,
                'cantidad_items': carrito.cantidad_items,
                'expira_en': carrito.expira_en,
                'creado_en': carrito.creado_en
            }
        return None
    
    def agregar_item_carrito(self, carrito_id: int, producto: Dict, 
                            cantidad: int = None, medidas: str = None, area: float = None,
                            precio_unitario: int = None, subtotal: int = None) -> bool:
        """Agrega un item al carrito"""
        session = self._get_session()
        try:
            # Debug
            print(f"[DEBUG] agregar_item_carrito: carrito_id={carrito_id}, producto={producto}, cantidad={cantidad}, medidas={medidas}, subtotal={subtotal}")
            
            # Preparar cantidad como string
            if medidas:
                cantidad_str = medidas
            elif cantidad:
                cantidad_str = str(cantidad)
            else:
                cantidad_str = "1"
            
            # Asegurar que subtotal sea un número válido
            subtotal_int = int(subtotal) if subtotal and subtotal > 0 else 0
            precio_int = int(precio_unitario) if precio_unitario and precio_unitario > 0 else 0
            
            print(f"[DEBUG] subtotal_int={subtotal_int}, precio_int={precio_int}")
            
            item = CarritoItem(
                carrito_id=carrito_id,
                producto_id=producto.get('prod_id') or producto.get('id'),
                nombre_producto=producto.get('nombre'),
                cantidad=cantidad_str,
                precio_unitario=precio_int,
                subtotal=subtotal_int
            )
            session.add(item)
            
            # Actualizar totales del carrito
            carrito = session.query(Carrito).filter(Carrito.id == carrito_id).first()
            if carrito:
                carrito.total = (carrito.total or 0) + subtotal_int
                carrito.cantidad_items = (carrito.cantidad_items or 0) + 1
                print(f"[DEBUG] Carrito actualizado: total={carrito.total}, items={carrito.cantidad_items}")
            
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] agregar_item_carrito: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def obtener_items_carrito(self, carrito_id: int) -> List[Dict]:
        """Obtiene los items de un carrito"""
        session = self._get_session()
        items = session.query(CarritoItem).filter(CarritoItem.carrito_id == carrito_id).all()
        session.close()
        
        return [{
            'id': item.id,
            'producto_id': item.producto_id,
            'nombre_producto': item.nombre_producto,
            'cantidad': item.cantidad,
            'precio_unitario': item.precio_unitario,
            'subtotal': item.subtotal
        } for item in items]
    
    def limpiar_carrito(self, carrito_id: int) -> bool:
        """Limpia todos los items de un carrito"""
        session = self._get_session()
        try:
            session.query(CarritoItem).filter(CarritoItem.carrito_id == carrito_id).delete()
            carrito = session.query(Carrito).filter(Carrito.id == carrito_id).first()
            if carrito:
                carrito.total = 0
                carrito.cantidad_items = 0
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] limpiar_carrito: {e}")
            return False
    
    # ============================================
    # PEDIDOS
    # ============================================
    
    def crear_pedido(self, carrito_id: int, cliente_id: str, usuario_id: str,
                     subtotal: int = None, total: int = None, cantidad_items: int = None,
                     nombre_comprador: str = None, telefono: str = None,
                     telefono_contacto: str = None, direccion: str = None) -> Optional[str]:
        """Crea un nuevo pedido desde un carrito"""
        session = self._get_session()
        try:
            # Generar número de orden único (con timestamp y random)
            import random
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = random.randint(1000, 9999)
            numero_orden = f"ORD-{timestamp}-{random_suffix}"
            
            # Usar telefono_contacto si se proporciona, sino telefono
            telefono_final = telefono_contacto if telefono_contacto else telefono
            
            pedido = Pedido(
                numero_orden=numero_orden,
                cliente_id=cliente_id,
                usuario_id=usuario_id,
                carrito_id=carrito_id,
                subtotal=subtotal or 0,
                total=total or 0,
                cantidad_items=cantidad_items or 0,
                nombre_comprador=nombre_comprador,
                telefono_contacto=telefono_final,
                direccion_entrega=direccion,
                estado='confirmado',
                confirmado_en=datetime.now()
            )
            session.add(pedido)
            session.commit()
            
            # Copiar items del carrito al pedido
            items_carrito = session.query(CarritoItem).filter(CarritoItem.carrito_id == carrito_id).all()
            for item in items_carrito:
                pedido_item = PedidoItem(
                    pedido_id=pedido.id,
                    producto_id=item.producto_id,
                    nombre_producto=item.nombre_producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    subtotal=item.subtotal
                )
                session.add(pedido_item)
            
            # Limpiar carrito
            self.limpiar_carrito(carrito_id)
            
            session.commit()
            session.close()
            return numero_orden
            
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] crear_pedido: {e}")
            return None
    
    def obtener_pedido(self, numero_orden: str) -> Optional[Dict]:
        """Obtiene un pedido por su número de orden"""
        session = self._get_session()
        pedido = session.query(Pedido).filter(Pedido.numero_orden == numero_orden).first()
        session.close()
        
        if pedido:
            return {
                'id': pedido.id,
                'numero_orden': pedido.numero_orden,
                'cliente_id': pedido.cliente_id,
                'usuario_id': pedido.usuario_id,
                'total': pedido.total,
                'estado': pedido.estado,
                'creado_en': pedido.creado_en
            }
        return None
    
    # ============================================
    # ESTADO DE USUARIO
    # ============================================
    
    def guardar_estado(self, cliente_id: str, user_id: str, estado: Dict) -> bool:
        """Guarda el estado de una conversación"""
        session = self._get_session()
        try:
            estado_db = session.query(EstadoUsuario).filter(
                EstadoUsuario.cliente_id == cliente_id,
                EstadoUsuario.usuario_id == user_id
            ).first()
            
            if estado_db:
                estado_db.paso = estado.get('paso', 0)
                estado_db.categoria = estado.get('categoria')
                estado_db.producto = estado.get('producto')
                estado_db.cantidad = str(estado.get('cantidad')) if estado.get('cantidad') else None
                estado_db.total = estado.get('total', 0)
                estado_db.datos_extra = json.dumps(estado.get('datos_extra', {}))
                estado_db.actualizado_en = datetime.now()
            else:
                estado_db = EstadoUsuario(
                    cliente_id=cliente_id,
                    usuario_id=user_id,
                    paso=estado.get('paso', 0),
                    categoria=estado.get('categoria'),
                    producto=estado.get('producto'),
                    cantidad=str(estado.get('cantidad')) if estado.get('cantidad') else None,
                    total=estado.get('total', 0),
                    datos_extra=json.dumps(estado.get('datos_extra', {}))
                )
                session.add(estado_db)
            
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] guardar_estado: {e}")
            return False
    
    def obtener_estado(self, cliente_id: str, user_id: str) -> Optional[Dict]:
        """Obtiene el estado de una conversación"""
        session = self._get_session()
        estado_db = session.query(EstadoUsuario).filter(
            EstadoUsuario.cliente_id == cliente_id,
            EstadoUsuario.usuario_id == user_id
        ).first()
        session.close()
        
        if estado_db:
            return {
                'paso': estado_db.paso,
                'categoria': estado_db.categoria,
                'producto': estado_db.producto,
                'cantidad': estado_db.cantidad,
                'total': estado_db.total,
                'datos_extra': json.loads(estado_db.datos_extra) if estado_db.datos_extra else {}
            }
        return None
    
    def limpiar_estado(self, cliente_id: str, user_id: str) -> bool:
        """Limpia el estado de un usuario"""
        session = self._get_session()
        try:
            session.query(EstadoUsuario).filter(
                EstadoUsuario.cliente_id == cliente_id,
                EstadoUsuario.usuario_id == user_id
            ).delete()
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] limpiar_estado: {e}")
            return False
    
    # ============================================
    # CONVERSACIONES
    # ============================================
    
    def guardar_conversacion(self, cliente_id: str, user_id: str, 
                            mensaje: str, respuesta: str, tipo: str) -> bool:
        """Guarda un mensaje de conversación para auditoría"""
        session = self._get_session()
        try:
            conv = Conversacion(
                cliente_id=cliente_id,
                user_id=user_id,
                mensaje=mensaje,
                respuesta=respuesta,
                tipo=tipo
            )
            session.add(conv)
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] guardar_conversacion: {e}")
            return False
    
    # ============================================
    # COMPROBANTES DE PAGO
    # ============================================
    
    def guardar_comprobante_pago(self, cliente_id: str, user_id: str, 
                                  pedido_id: str, imagen_data: str) -> int:
        """Guarda un comprobante de pago"""
        session = self._get_session()
        try:
            comprobante = ComprobantePago(
                cliente_id=cliente_id,
                user_id=user_id,
                pedido_id=pedido_id,
                imagen_data=imagen_data
            )
            session.add(comprobante)
            session.commit()
            comprobante_id = comprobante.id
            session.close()
            return comprobante_id
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] guardar_comprobante_pago: {e}")
            return 0
    
    def obtener_comprobantes_pendientes(self, cliente_id: str) -> List[Dict]:
        """Obtiene comprobantes pendientes de verificación"""
        session = self._get_session()
        comprobantes = session.query(ComprobantePago).filter(
            ComprobantePago.cliente_id == cliente_id,
            ComprobantePago.estado == 'pendiente'
        ).all()
        session.close()
        
        return [{
            'id': c.id,
            'pedido_id': c.pedido_id,
            'user_id': c.user_id,
            'fecha_envio': c.fecha_envio
        } for c in comprobantes]
    
    def verificar_comprobante(self, comprobante_id: int, admin: str, estado: str) -> bool:
        """Marca un comprobante como verificado o rechazado"""
        session = self._get_session()
        try:
            comprobante = session.query(ComprobantePago).filter(ComprobantePago.id == comprobante_id).first()
            if comprobante:
                comprobante.estado = estado
                comprobante.verificado_por = admin
                comprobante.fecha_verificacion = datetime.now()
                session.commit()
                session.close()
                return True
            session.close()
            return False
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] verificar_comprobante: {e}")
            return False
    
    # ============================================
    # MODO USUARIO (Bot/Humano)
    # ============================================
    
    def obtener_modo_usuario(self, cliente_id: str, user_id: str) -> str:
        """Obtiene el modo actual del usuario (bot o humano)"""
        session = self._get_session()
        try:
            modo = session.query(ModoUsuario).filter(
                ModoUsuario.cliente_id == cliente_id,
                ModoUsuario.user_id == user_id
            ).first()
            session.close()
            return modo.modo if modo else 'bot'
        except Exception as e:
            session.close()
            print(f"[ERROR] obtener_modo_usuario: {e}")
            return 'bot'
    
    def set_modo_usuario(self, cliente_id: str, user_id: str, modo: str, activado_por: str = 'sistema') -> bool:
        """Cambia el modo del usuario (bot o humano)"""
        session = self._get_session()
        try:
            modo_db = session.query(ModoUsuario).filter(
                ModoUsuario.cliente_id == cliente_id,
                ModoUsuario.user_id == user_id
            ).first()
            
            if modo_db:
                modo_db.modo = modo
                modo_db.activado_por = activado_por
                modo_db.fecha_cambio = datetime.now()
            else:
                modo_db = ModoUsuario(
                    cliente_id=cliente_id,
                    user_id=user_id,
                    modo=modo,
                    activado_por=activado_por
                )
                session.add(modo_db)
            
            session.commit()
            session.close()
            return True
        except Exception as e:
            session.rollback()
            session.close()
            print(f"[ERROR] set_modo_usuario: {e}")
            return False
    
    def guardar_mensaje_asesor(self, cliente_id: str, user_id: str, mensaje: str, asesor: str) -> bool:
        """Guarda un mensaje del asesor para enviar al usuario"""
        # Por ahora, solo logueamos - la implementación completa requeriría una tabla adicional
        print(f"[MODO HUMANO] Mensaje de {asesor} para {user_id}: {mensaje[:50]}...")
        return True
    
    def obtener_mensajes_pendientes_asesor(self, cliente_id: str, user_id: str) -> List[Dict]:
        """Obtiene mensajes pendientes del asesor para el usuario"""
        # Implementación básica - retorna lista vacía
        return []


# Instancia global
db_saas = DatabaseSaaS()
