"""
carrito_bot.py - Funciones del carrito de compras para el bot
Integra el carrito SaaS con el flujo del bot
"""

from typing import Dict, Tuple
from database.database_saas import db_saas

class CarritoBot:
    """Gestiona el carrito de compras dentro del flujo del bot"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def agregar_producto(self, cliente_id: str, user_id: str, 
                        estado: Dict, area: int = None) -> str:
        """Agrega un producto al carrito y retorna mensaje para el usuario"""
        
        # Obtener o crear carrito
        carrito = db_saas.obtener_carrito_activo(cliente_id, user_id)
        if not carrito:
            return "❌ Error al crear carrito. Intente de nuevo."
        
        carrito_id = carrito['id']
        
        # Obtener información del producto
        cat_id = estado.get('categoria')
        prod_idx = estado.get('producto')
        cantidad = estado.get('cantidad')
        total = estado.get('total')
        
        categorias = self.config.get('categorias', {})
        cat = categorias.get(cat_id, {})
        tipos = cat.get('tipos', [])
        
        if prod_idx >= len(tipos):
            return "❌ Error: Producto no encontrado."
        
        producto = tipos[prod_idx]
        
        # Preparar datos según tipo de cotización
        tipo_cot = cat.get('tipo_cotizacion', 'cantidad')
        
        if tipo_cot == 'medida' and area:
            # Producto por medida
            cantidad_num = None
            medidas = cantidad  # Ej: "100x200cm"
            area_cm2 = area
        else:
            # Producto por cantidad
            cantidad_num = cantidad if isinstance(cantidad, int) else 1
            medidas = None
            area_cm2 = None
        
        # Calcular precio unitario
        if area_cm2:
            precio_unitario = int(total / area_cm2) if area_cm2 > 0 else 0
        elif cantidad_num and cantidad_num > 0:
            precio_unitario = int(total / cantidad_num)
        else:
            precio_unitario = total
        
        # Agregar al carrito
        db_saas.agregar_item_carrito(
            carrito_id=carrito_id,
            producto={
                'categoria_id': cat_id,
                'prod_id': producto.get('id', ''),
                'nombre': producto.get('nombre', '')
            },
            cantidad=cantidad_num,
            medidas=medidas,
            area=area_cm2,
            precio_unitario=precio_unitario
        )
        
        # Generar mensaje de confirmación
        if area_cm2:
            cantidad_str = f"{medidas} ({area_cm2:,} cm²)"
        else:
            cantidad_str = f"{cantidad_num:,} unidades"
        
        tiempo_entrega = self._calcular_tiempo_entrega(cat_id, cantidad_num or 0)
        
        return f"""✅ AGREGADO AL CARRITO

• {producto.get('nombre')}
• Cantidad: {cantidad_str}
• Subtotal: ${total:,} COP
• Entrega: {tiempo_entrega}

🛒 ¿Qué deseas hacer?
1️⃣ Agregar OTRO producto
2️⃣ VER carrito / Finalizar
3️⃣ CANCELAR

Escribe 1, 2 o 3."""
    
    def ver_carrito(self, cliente_id: str, user_id: str) -> str:
        """Muestra el contenido del carrito"""
        carrito = db_saas.obtener_carrito_activo(cliente_id, user_id)
        
        if not carrito or carrito['cantidad_items'] == 0:
            return "🛒 Tu carrito está vacío.\n\nEscribe 'menu' para ver productos."
        
        carrito_id = carrito['id']
        items = db_saas.obtener_items_carrito(carrito_id)
        
        mensaje = "🛒 TU CARRITO\n\n"
        
        for i, item in enumerate(items, 1):
            if item['medidas']:
                cantidad_str = f"{item['medidas']}"
            else:
                cantidad_str = f"{item['cantidad']:,} unid"
            
            mensaje += f"{i}. {item['nombre_producto']}\n"
            mensaje += f"   {cantidad_str} × ${item['precio_unitario']:,} = ${item['subtotal']:,}\n\n"
        
        mensaje += f"💰 TOTAL: ${carrito['total']:,} COP\n\n"
        mensaje += "¿Confirmar pedido? Escribe 'SI' para confirmar o 'AGREGAR' para más productos."
        
        return mensaje
    
    def finalizar_pedido(self, cliente_id: str, user_id: str, 
                        nombre: str = None, telefono: str = None) -> str:
        """Convierte el carrito en pedido"""
        carrito = db_saas.obtener_carrito_activo(cliente_id, user_id)
        
        if not carrito or carrito['cantidad_items'] == 0:
            return "❌ No hay productos en el carrito."
        
        # Crear pedido
        numero_orden = db_saas.crear_pedido(
            carrito_id=carrito['id'],
            cliente_id=cliente_id,
            usuario_id=user_id,
            nombre_comprador=nombre,
            telefono_contacto=telefono
        )
        
        if not numero_orden:
            return "❌ Error al crear el pedido. Intente de nuevo."
        
        return f"""🎉 ¡PEDIDO CONFIRMADO!

Número de orden: {numero_orden}
Total: ${carrito['total']:,} COP

Gracias por tu compra. Te contactaremos pronto para confirmar los detalles.

¿Deseas hacer otro pedido? Escribe 'menu'."""
    
    def _calcular_tiempo_entrega(self, categoria_id: str, cantidad: int) -> str:
        """Calcula tiempo de entrega según categoría"""
        # Tiempos específicos para Cajas
        if categoria_id == "cajas":
            if cantidad <= 2000:
                return "5-10 días hábiles"
            elif cantidad <= 5000:
                return "7-15 días hábiles"
            elif cantidad <= 8000:
                return "10-20 días hábiles"
            else:
                return "15-25 días hábiles"
        
        # Default para otras categorías
        return self.config.get('tiempo_entrega_default', '2-5 días hábiles')
