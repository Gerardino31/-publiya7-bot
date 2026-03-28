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
    
    def _calcular_descuento_info(self, producto: Dict, cantidad: int, total: int) -> Dict:
        """Calcula información del descuento aplicado para mostrar al cliente"""
        precio_1000 = producto.get('precio_1000', 0)
        
        if cantidad >= 5000 and 'precio_5000' in producto:
            # 10% de descuento para 5000+
            precio_sin_descuento = int((precio_1000 / 1000) * cantidad)
            ahorro = precio_sin_descuento - total
            return {
                'tiene_descuento': True,
                'porcentaje': 10,
                'ahorro': ahorro,
                'precio_sin_descuento': precio_sin_descuento
            }
        elif cantidad >= 2000 and 'precio_2000' in producto:
            # 5% de descuento para 2000+
            precio_sin_descuento = int((precio_1000 / 1000) * cantidad)
            ahorro = precio_sin_descuento - total
            return {
                'tiene_descuento': True,
                'porcentaje': 5,
                'ahorro': ahorro,
                'precio_sin_descuento': precio_sin_descuento
            }
        
        return {'tiene_descuento': False}
    
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
        
        # Calcular información de descuento
        descuento_info = self._calcular_descuento_info(producto, cantidad_num or 0, total)
        
        # Obtener resumen actual del carrito (después de agregar el item)
        carrito_actualizado = db_saas.obtener_carrito_por_id(carrito_id)
        items = db_saas.obtener_items_carrito(carrito_id)
        total_carrito = carrito_actualizado['total'] if carrito_actualizado else 0
        
        # Construir mensaje con saltos de línea reales
        lineas = [
            "✅ PRODUCTO AGREGADO",
            "",
            f"• {producto.get('nombre')}",
            f"• Cantidad: {cantidad_str}",
        ]
        
        # Agregar información de descuento si aplica
        if descuento_info['tiene_descuento']:
            lineas.extend([
                f"• 💵 Precio normal: ${descuento_info['precio_sin_descuento']:,} COP",
                f"• 🏷️ Descuento: {descuento_info['porcentaje']}%",
                f"• 💰 Subtotal: ${total:,} COP",
                f"• 💚 Ahorro: ${descuento_info['ahorro']:,} COP",
            ])
        else:
            lineas.append(f"• Subtotal: ${total:,} COP")
        
        lineas.extend([
            f"• Entrega: {tiempo_entrega}",
            "",
            f"🛒 CARRITO ACTUAL ({len(items)} productos):",
            f"💰 Total: ${total_carrito:,} COP",
            "",
            "¿Qué deseas hacer?",
            "1️⃣ Agregar OTRO producto",
            "2️⃣ VER carrito completo",
            "3️⃣ FINALIZAR pedido",
            "4️⃣ CANCELAR carrito",
            "",
            "Escribe 1, 2, 3 o 4."
        ]
        
        return "\n".join(lineas)
    
    def ver_carrito(self, cliente_id: str, user_id: str, mostrar_resumen: bool = False) -> str:
        """Muestra el contenido del carrito o el resumen final"""
        carrito = db_saas.obtener_carrito_activo(cliente_id, user_id)
        
        if not carrito or carrito['cantidad_items'] == 0:
            return "🛒 Tu carrito está vacío.\n\nEscribe 'menu' para ver productos."
        
        carrito_id = carrito['id']
        items = db_saas.obtener_items_carrito(carrito_id)
        
        lineas = []
        
        if mostrar_resumen:
            lineas.append("🧾 RESUMEN DE TU PEDIDO")
        else:
            lineas.append("🛒 TU CARRITO")
        
        lineas.append("")
        
        for i, item in enumerate(items, 1):
            if item['medidas']:
                cantidad_str = f"{item['medidas']}"
            else:
                cantidad_str = f"{item['cantidad']:,} unid"
            
            lineas.append(f"{i}. {item['nombre_producto']}")
            lineas.append(f"   {cantidad_str} × ${item['precio_unitario']:,} = ${item['subtotal']:,}")
            lineas.append("")
        
        lineas.append(f"💰 TOTAL: ${carrito['total']:,} COP")
        lineas.append("")
        
        if mostrar_resumen:
            lineas.append("¿Confirmas tu pedido?")
            lineas.append("1️⃣ Sí, confirmar")
            lineas.append("2️⃣ No, seguir comprando")
            lineas.append("3️⃣ Cancelar todo")
        else:
            lineas.append("¿Qué deseas hacer?")
            lineas.append("1️⃣ Agregar OTRO producto")
            lineas.append("2️⃣ VER carrito completo")
            lineas.append("3️⃣ FINALIZAR pedido")
            lineas.append("4️⃣ CANCELAR carrito")
        
        return "\n".join(lineas)
    
    def cancelar_carrito(self, cliente_id: str, user_id: str) -> str:
        """Cancela el carrito activo"""
        carrito = db_saas.obtener_carrito_activo(cliente_id, user_id)
        
        if not carrito or carrito['cantidad_items'] == 0:
            return "🛒 No tienes productos en el carrito.\n\nEscribe 'menu' para ver productos."
        
        # Limpiar items del carrito
        db_saas.limpiar_carrito(carrito['id'])
        
        return "❌ Carrito cancelado.\n\nTodos los productos han sido eliminados.\n\nEscribe 'menu' para empezar de nuevo."
    
    def finalizar_pedido(self, cliente_id: str, user_id: str, 
                        nombre: str = None, telefono: str = None) -> str:
        """Convierte el carrito en pedido y envía notificaciones"""
        from app.notificaciones import notificador
        
        # DEBUG: Verificar configuración
        print(f"[DEBUG] CarritoBot.finalizar_pedido - cliente_id: {cliente_id}")
        print(f"[DEBUG] Config email_notificaciones: '{self.config.get('email_notificaciones')}'")
        print(f"[DEBUG] Config email: '{self.config.get('email')}'")
        
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
        
        # Obtener items para notificación
        items = db_saas.obtener_items_carrito(carrito['id'])
        
        # Enviar notificación al dueño
        pedido_data = {
            'numero_orden': numero_orden,
            'total': carrito['total'],
            'usuario_id': user_id,
            'nombre_comprador': nombre
        }
        
        # Configuración del cliente para notificaciones
        cliente_config = {
            'nombre': self.config.get('nombre', 'Negocio'),
            'email': self.config.get('email'),
            'email_notificaciones': self.config.get('email_notificaciones'),
            'whatsapp': self.config.get('whatsapp'),
            'telefono_notificaciones': self.config.get('telefono_notificaciones'),
            'notificar_whatsapp': True
        }
        
        # Enviar notificación (no bloquea la respuesta al usuario)
        try:
            notificador.notificar_nuevo_pedido(cliente_config, pedido_data, items)
        except Exception as e:
            print(f"⚠️ Error en notificación: {e}")
        
        # Construir mensaje de confirmación con métodos de pago
        lineas = [
            "🎉 ¡PEDIDO CONFIRMADO!",
            "",
            f"📦 Número de orden: *{numero_orden}*",
            f"💰 Total: ${carrito['total']:,} COP",
            "",
            "Gracias por tu compra. Aquí tienes los métodos de pago disponibles:",
            ""
        ]
        
        # Agregar métodos de pago configurados
        metodos_pago = []
        
        # Nequi/Daviplata
        nequi_numero = self.config.get('nequi_numero', self.config.get('whatsapp', ''))
        if nequi_numero:
            metodos_pago.append(f"📱 *Nequi/Daviplata:* {nequi_numero}")
        
        # Transferencia bancaria
        banco_nombre = self.config.get('banco_nombre', '')
        banco_tipo = self.config.get('banco_tipo_cuenta', '')
        banco_cuenta = self.config.get('banco_numero_cuenta', '')
        if banco_nombre and banco_cuenta:
            tipo_cuenta = "Ahorros" if banco_tipo == "ahorros" else "Corriente"
            metodos_pago.append(f"🏦 *{banco_nombre}* - Cuenta {tipo_cuenta}")
            metodos_pago.append(f"   Número: {banco_cuenta}")
        
        # Efectivo
        acepta_efectivo = self.config.get('acepta_efectivo', 'si')
        if acepta_efectivo == 'si':
            metodos_pago.append("💵 *Efectivo:* Contra entrega")
        
        if metodos_pago:
            lineas.append("💳 *MÉTODOS DE PAGO:*")
            lineas.extend(metodos_pago)
            lineas.append("")
        
        lineas.extend([
            "📸 *Por favor envía el comprobante de pago* respondiendo a este mensaje con la imagen.",
            "",
            "¿Deseas hacer otro pedido? Escribe 'menu'."
        ])
        
        return "\n".join(lineas)
    
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
