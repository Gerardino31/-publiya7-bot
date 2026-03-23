"""
Bot Multi-Cliente SaaS - Estructura para múltiples imprentas
Cada cliente tiene su propia configuración JSON
"""

import json
import os
from datetime import datetime
import random

class BotMultiCliente:
    """
    Bot genérico que carga configuración según el cliente.
    Mismo código, diferentes productos/precios por cliente.
    """
    
    def __init__(self, cliente_id="publiya7"):
        self.cliente_id = cliente_id
        self.config = self._cargar_config(cliente_id)
        self.reset()
    
    def _cargar_config(self, cliente_id):
        """Carga la configuración específica del cliente."""
        config_path = f"clientes/configs/{cliente_id}.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: No se encontró config para {cliente_id}")
            return None
    
    def reset(self):
        """Reinicia el estado de la conversación."""
        self.paso = 0
        self.categoria = None
        self.producto = None
        self.cantidad = None
        self.total = 0
    
    # ========== FUNCIONES DE CORTESÍA (reutilizables) ==========
    
    def _obtener_saludo_horario(self):
        """Saludo personalizado según hora y cliente."""
        hora = datetime.now().hour
        nombre = self.config['nombre']
        
        if 6 <= hora < 12:
            return f"¡Buenos días! ☀️ Bienvenido a {nombre}."
        elif 12 <= hora < 18:
            return f"¡Buenas tardes! 🌤️ Gracias por contactar a {nombre}."
        else:
            return f"¡Buenas noches! 🌙 {nombre} a su servicio."
    
    def _frases_cortesia(self, tipo="general"):
        """Frases de cortesía personalizables por cliente."""
        frases = {
            "general": [
                "Con mucho gusto le ayudo...",
                "Será un placer atenderle...",
                f"En {self.config['nombre']} estamos para servirle..."
            ],
            "cotizando": [
                "Permítame preparar su cotización...",
                "Un momento mientras calculo...",
                "Déjeme buscarle la mejor opción..."
            ],
            "despedida": [
                f"Gracias por preferir {self.config['nombre']}.",
                "Ha sido un gusto atenderle.",
                "Estamos a sus órdenes para cualquier consulta."
            ]
        }
        return random.choice(frases.get(tipo, frases["general"]))
    
    # ========== MENÚS DINÁMICOS ==========
    
    def _generar_menu_principal(self):
        """Genera menú principal según categorías del cliente."""
        saludo = self._obtener_saludo_horario()
        eslogan = self.config.get('eslogan', '')
        
        menu = f"""{saludo}

{eslogan}

{self._frases_cortesia('general')}

¿Qué producto le interesa?"""
        
        # Agregar categorías dinámicamente
        for i, (cat_id, cat_data) in enumerate(self.config['categorias'].items(), 1):
            menu += f"\n{i}️⃣ {cat_data['nombre']}"
        
        menu += "\n\nEscriba el número de la categoría que necesite."
        return menu
    
    def _generar_menu_categoria(self, categoria_id):
        """Genera menú de productos para una categoría específica."""
        cat = self.config['categorias'][categoria_id]
        
        menu = f"📋 {cat['nombre'].upper()}\n\n"
        
        for i, producto in enumerate(cat['tipos'], 1):
            menu += f"{i}. {producto['nombre']}"
            
            # Mostrar precio según tipo de cotización
            if cat['tipo_cotizacion'] == 'cantidad':
                if 'precio_1000' in producto:
                    menu += f" - ${producto['precio_1000']:,} por 1000"
            elif cat['tipo_cotizacion'] == 'medida':
                precio_unidad = producto.get('precio_m2', producto.get('precio_cm2', 0))
                unidad = cat.get('unidad', 'unidad')
                menu += f" - ${precio_unidad:,}/{unidad}"
            
            menu += "\n"
        
        return menu
    
    # ========== CÁLCULO DE PRECIOS ==========
    
    def _calcular_precio(self, categoria_id, producto_id, cantidad):
        """Calcula precio según configuración del cliente."""
        cat = self.config['categorias'][categoria_id]
        producto = cat['tipos'][producto_id]
        
        if cat['tipo_cotizacion'] == 'cantidad':
            # Lógica para productos por cantidad
            base = cat.get('unidad_base', 1000)
            
            # Buscar precio según cantidad
            if cantidad >= 5000 and 'precio_5000' in producto:
                precio_base = producto['precio_5000']
            elif cantidad >= 2000 and 'precio_2000' in producto:
                precio_base = producto['precio_2000']
            else:
                precio_base = producto.get('precio_1000', 0)
            
            # Calcular proporcional
            return int(precio_base * (cantidad / base))
        
        elif cat['tipo_cotizacion'] == 'medida':
            # Lógica para productos por medida (m2 o cm2)
            precio_unidad = producto.get('precio_m2', producto.get('precio_cm2', 0))
            return int(cantidad * precio_unidad)
        
        return 0
    
    # ========== PROCESAMIENTO DE MENSAJES ==========
    
    def procesar(self, mensaje):
        """Procesa mensajes del cliente."""
        msg = mensaje.lower().strip()
        
        # Saludos
        if any(x in msg for x in ["hola", "buenas", "hey"]):
            return self._generar_menu_principal()
        
        # PASO 0: Seleccionar categoría
        if self.paso == 0:
            # Buscar categoría por número o nombre
            for i, (cat_id, cat_data) in enumerate(self.config['categorias'].items(), 1):
                if str(i) in msg or cat_id in msg:
                    self.categoria = cat_id
                    self.paso = 1
                    return self._generar_menu_categoria(cat_id)
            
            return f"Disculpe, no reconocí esa categoría. {self._frases_cortesia('general')}"
        
        # PASO 1: Seleccionar producto
        if self.paso == 1:
            try:
                opcion = int(msg) - 1
                cat = self.config['categorias'][self.categoria]
                if 0 <= opcion < len(cat['tipos']):
                    self.producto = opcion
                    self.paso = 2
                    producto = cat['tipos'][opcion]
                    return f"✅ {producto['nombre']}\n\n{self._frases_cortesia('cotizando')}\n\n¿Qué cantidad necesita?"
            except:
                pass
            return "Por favor seleccione el número del producto."
        
        # PASO 2: Ingresar cantidad
        if self.paso == 2:
            try:
                cantidad = int(msg)
                self.cantidad = cantidad
                self.total = self._calcular_precio(self.categoria, self.producto, cantidad)
                self.paso = 3
                return self._generar_cotizacion()
            except:
                return "Por favor indique una cantidad válida."
        
        # PASO 3: Confirmar pedido
        if self.paso == 3:
            if msg in ["si", "sí"]:
                # Guardar en base de datos con cliente_id
                # self.db.guardar_pedido(self.cliente_id, ...)
                self.reset()
                return f"🎉 ¡Pedido confirmado! {self._frases_cortesia('despedida')}"
            elif msg == "no":
                self.reset()
                return f"Entendido. {self._frases_cortesia('general')}"
        
        return "No entendí. Escriba 'hola' para comenzar."
    
    def _generar_cotizacion(self):
        """Genera cotización final."""
        cat = self.config['categorias'][self.categoria]
        producto = cat['tipos'][self.producto]
        
        return f"""📏 COTIZACIÓN

• Producto: {producto['nombre']}
• Cantidad: {self.cantidad:,}
• Total: ${self.total:,} {self.config['moneda']}

⏱️ Tiempo de entrega: {self.config.get('tiempo_entrega_default', 'Consultar')}

¿Confirma el pedido? (sí/no)"""


# ========== EJEMPLO DE USO ==========
if __name__ == "__main__":
    # Crear bot para Publiya7
    bot_publiya7 = BotMultiCliente("publiya7")
    
    # Crear bot para Imprenta XYZ
    bot_xyz = BotMultiCliente("imprentaxyz")
    
    print("="*60)
    print("BOT MULTI-CLIENTE SAAS")
    print("="*60)
    print("\n1. Publiya7 (Medellín):")
    print(bot_publiya7.procesar("hola"))
    
    print("\n" + "="*60)
    print("\n2. Imprenta XYZ (Bogotá):")
    print(bot_xyz.procesar("hola"))
