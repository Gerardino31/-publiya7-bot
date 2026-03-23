# Bot Engine - Motor de cotización para imprentas
# Versión 2.0 - Soporta múltiples tipos de productos
# Desarrollado por: Andres

import json
import re
from typing import Dict, Tuple, Optional

class BotEngine:
    """
    Motor de bot para cotizaciones de imprenta.
    Cada instancia maneja un cliente específico.
    """
    
    def __init__(self, cliente_id: str):
        """
        Inicializa el bot para un cliente específico.
        
        Args:
            cliente_id: Identificador único del cliente (ej: "publiya7")
        """
        self.cliente_id = cliente_id
        self.config = self._cargar_config()
        
        # Estado de la conversación
        self.paso = 0  # 0=inicio, 1=esperando_cantidad, 2=esperando_medidas, 3=listo_para_cotizar
        self.producto = None
        self.tipo_producto = None  # 'cantidad', 'medida', 'personalizado'
        self.ancho = None
        self.alto = None
        self.cantidad = None
        self.area = None
        self.es_cm = False
        self.total = 0
    
    def _cargar_config(self) -> Dict:
        """Carga la configuración del cliente desde JSON."""
        try:
            with open(f'clientes/configs/{self.cliente_id}.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuración por defecto
            return {
                "nombre_empresa": "Imprenta",
                "telefono": "+57 XXX XXX XXXX",
                "precios": {
                    "gran_formato_m2": 94000
                },
                "productos": {
                    "adhesivo": "Adhesivo"
                }
            }
    
    def _detectar_tipo_producto(self, producto_nombre: str) -> str:
        """
        Detecta si el producto se cotiza por cantidad, medida o es personalizado.
        """
        producto_lower = producto_nombre.lower()
        
        # Productos personalizados
        personalizados = ["camiseta", "camisetas", "polo", "polos"]
        if any(p in producto_lower for p in personalizados):
            return "personalizado"
        
        # Productos por cantidad (no requieren medidas)
        por_cantidad = ["tarjeta", "tarjetas", "volante", "volantes", "flyer", "flyers", 
                       "etiqueta", "etiquetas", "talonario", "talonarios", "sello", "sellos",
                       "afiche", "afiches", "plegable", "plegables", "membrete", "membretes",
                       "carnet", "carnets", "pad", "mouse", "souvenir", "souvenirs",
                       "tula", "tulas", "termo", "termos", "caja", "cajas"]
        if any(p in producto_lower for p in por_cantidad):
            return "cantidad"
        
        # Productos por medida (gran formato)
        return "medida"
    
    def _detectar_tipo_tarjeta(self, mensaje: str) -> Optional[str]:
        """Detecta el tipo de tarjeta que quiere el cliente."""
        msg = mensaje.lower()
        
        if "sencilla" in msg or "brillo uv" in msg or "barniz uv" in msg:
            if "2 caras" in msg or "dos caras" in msg or "ambas caras" in msg:
                return "sencilla_brillo_uv_2_caras"
            return "sencilla_brillo_uv_1_cara"
        
        if "mate" in msg:
            if "reserva" in msg:
                if "2 caras" in msg or "dos caras" in msg:
                    return "mate_con_reserva_2_caras"
                return "mate_con_reserva_1_cara"
            if "2 caras" in msg or "dos caras" in msg:
                return "mate_2_caras"
            return "mate_1_cara"
        
        if "estampada" in msg or "estampado" in msg:
            if "2 lados" in msg or "dos lados" in msg or "ambos lados" in msg:
                return "estampada_2_lados"
            return "estampada_1_lado"
        
        if "laminada" in msg or "plastificada" in msg:
            return "lamindada"
        
        return None
    
    def _generar_menu_tarjetas(self) -> str:
        """Genera el menú de tipos de tarjetas."""
        return """📋 TIPOS DE TARJETAS DE PRESENTACIÓN (1000 unidades):

1️⃣  Sencilla Brillo UV:
   • 1 cara: $75.000 COP
   • 2 caras: $85.000 COP

2️⃣  Mate:
   • 1 cara: $119.000 COP
   • 2 caras: $130.000 COP

3️⃣  Mate con Reserva UV:
   • 1 cara: $145.000 COP
   • 2 caras: $165.000 COP

4️⃣  Estampada (Dorado/Plateado):
   • 1 lado: $350.000 COP
   • 2 lados: $380.000 COP

5️⃣  Laminada:
   • $390.000 COP

¿Qué tipo de tarjeta necesitas?"""
    
    def _calcular_precio_tarjeta(self, tipo_tarjeta: str, cantidad: int) -> Tuple[int, str]:
        """Calcula el precio según tipo de tarjeta y cantidad."""
        precios_base = {
            "sencilla_brillo_uv_1_cara": 75000,
            "sencilla_brillo_uv_2_caras": 85000,
            "mate_1_cara": 119000,
            "mate_2_caras": 130000,
            "mate_con_reserva_1_cara": 145000,
            "mate_con_reserva_2_caras": 165000,
            "estampada_1_lado": 350000,
            "estampada_2_lados": 380000,
            "lamindada": 390000
        }
        
        precio_base = precios_base.get(tipo_tarjeta, 75000)
        
        # Ajustar precio según cantidad (escala)
        if cantidad >= 5000:
            factor = 0.85  # 15% descuento
        elif cantidad >= 3000:
            factor = 0.90  # 10% descuento
        elif cantidad >= 2000:
            factor = 0.95  # 5% descuento
        else:
            factor = 1.0
        
        total = int(precio_base * factor * (cantidad / 1000))
        precio_str = f"${precio_base:,} COP base por 1000 unidades"
        
        if factor < 1.0:
            precio_str += f" (Descuento {int((1-factor)*100)}% aplicado)"
        
        return total, precio_str
    
    def _calcular_precio_medida(self, ancho: float, alto: float, es_cm: bool) -> Tuple[float, float]:
        """
        Calcula el precio según las medidas (para gran formato).
        """
        if es_cm:
            # Convertir cm a metros
            ancho_m = ancho / 100
            alto_m = alto / 100
            area_m2 = ancho_m * alto_m
            # Calcular usando precio por cm²
            area_cm2 = ancho * alto
            precio_cm2 = self.config['precios']['gran_formato'].get('adhesivo', {}).get('laminado_cm2', 9.4)
            total = area_cm2 * precio_cm2
        else:
            # Medidas en metros
            area_m2 = ancho * alto
            precio_m2 = self.config['precios']['gran_formato'].get('banner', {}).get('cm2_con_terminado', 8.5) * 10000 / 10000 * 10000
            # Simplificar: usar precio por m2 directo
            precio_m2 = 94000  # Default
            total = area_m2 * precio_m2
        
        return area_m2, total
    
    def detectar_medidas(self, mensaje: str) -> Optional[Tuple[float, float, bool]]:
        """
        Detecta medidas en el mensaje del cliente.
        """
        # Buscar en centímetros
        match = re.search(
            r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|centimetros?)',
            mensaje.lower()
        )
        if match:
            return float(match.group(1)), float(match.group(2)), True
        
        # Buscar en metros
        match = re.search(
            r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:m|metros?)?',
            mensaje.lower()
        )
        if match:
            return float(match.group(1)), float(match.group(2)), False
        
        return None
    
    def detectar_cantidad(self, mensaje: str) -> Optional[int]:
        """
        Detecta cantidad numérica en el mensaje.
        """
        # Buscar números seguidos de unidades o cantidades
        match = re.search(r'(\d+)\s*(?:unid|unidades|uds|cajas|etiquetas)?', mensaje.lower())
        if match:
            return int(match.group(1))
        return None
    
    def detectar_producto(self, mensaje: str) -> Optional[str]:
        """
        Detecta qué producto quiere el cliente.
        """
        productos = self.config.get('productos', {})
        mensaje_lower = mensaje.lower()
        
        for clave, nombre in productos.items():
            if clave in mensaje_lower:
                return nombre
        
        return None
    
    def procesar_mensaje(self, mensaje: str) -> str:
        """
        Procesa un mensaje del cliente y genera respuesta.
        """
        msg = mensaje.strip().lower()
        
        # ========== COMANDOS ESPECIALES ==========
        if any(saludo in msg for saludo in ["hola", "buenos dias", "buenas tardes", "buenas noches", "buenas", "hey", "saludos"]):
            return f"¡Hola! 👋 Bienvenido a {self.config['nombre_empresa']}.\n\nSoy tu asistente virtual y estoy aquí para ayudarte con tus cotizaciones.\n\n¿En qué puedo ayudarte hoy? Puedes preguntarme por:\n• Tarjetas de presentación\n• Volantes, flyers, afiches\n• Banners, adhesivos, vinilos\n• Etiquetas, cajas, sellos\n• O cualquier otro producto"
        
        if msg in ["menu", "opciones", "ayuda"]:
            return self._generar_menu()
        
        if msg in ["precio", "precios"]:
            return self._generar_precios()
        
        if msg in ["contacto", "telefono", "whatsapp", "email"]:
            return self.config.get('mensajes', {}).get('contacto', 
                f"📞 {self.config['telefono']} | 📧 {self.config['email']}")
        
        # ========== PASO 3: Mostrar cotización ==========
        if self.paso == 3:
            if msg in ["si", "sí", "confirmo", "ok", "dale"]:
                self._resetear_estado()
                return self._generar_confirmacion()
            elif msg in ["no", "cancelar", "modificar"]:
                self.paso = 1
                return "Entendido. ¿Quieres cambiar algo? Indícame los nuevos datos."
            else:
                return "¿Confirmas el pedido? Escribe 'si' para continuar o 'no' para modificar."
        
        # ========== PASO 2: Esperando tipo de tarjeta (solo para tarjetas) ==========
        if self.paso == 2:
            # Si es tarjeta, primero preguntar el tipo
            if self.producto and "tarjeta" in self.producto.lower():
                tipo_tarjeta = self._detectar_tipo_tarjeta(mensaje)
                if tipo_tarjeta:
                    self.tipo_tarjeta = tipo_tarjeta
                    self.paso = 2.5  # Nuevo paso para esperar cantidad
                    return f"✅ Tipo de tarjeta: {tipo_tarjeta}\n\n📦 ¿Qué cantidad necesitas?\n• Ejemplo: '1000 unidades'"
                else:
                    return self._generar_menu_tarjetas()
            
            # Si es cantidad normal
            if self.tipo_producto == "cantidad":
                cantidad = self.detectar_cantidad(mensaje)
                if cantidad:
                    self.cantidad = cantidad
                    self.total, precio_str = self._calcular_precio_cantidad(self.producto, cantidad)
                    self.paso = 3
                    return self._generar_cotizacion_cantidad(precio_str)
                else:
                    return "Por favor indica la cantidad que necesitas. Ejemplo: '5000 unidades'"
            
            elif self.tipo_producto == "medida":
                medidas = self.detectar_medidas(mensaje)
                if medidas:
                    ancho, alto, es_cm = medidas
                    self.ancho = ancho
                    self.alto = alto
                    self.es_cm = es_cm
                    self.area, self.total = self._calcular_precio_medida(ancho, alto, es_cm)
                    self.paso = 3
                    return self._generar_cotizacion_medida()
                else:
                    return "Por favor indica las medidas. Ejemplo: '2x3 metros' o '100x200 cm'"
        
        # ========== PASO 1: Detectar producto ==========
        producto = self.detectar_producto(mensaje)
        if producto:
            self.producto = producto
            self.tipo_producto = self._detectar_tipo_producto(producto)
            
            if self.tipo_producto == "personalizado":
                return self._generar_mensaje_personalizado()
            
            elif self.tipo_producto == "cantidad":
                # Verificar si ya incluye cantidad
                cantidad = self.detectar_cantidad(mensaje)
                if cantidad:
                    self.cantidad = cantidad
                    self.total, precio_str = self._calcular_precio_cantidad(producto, cantidad)
                    self.paso = 3
                    return self._generar_cotizacion_cantidad(precio_str)
                else:
                    self.paso = 2
                    return f"✅ Producto: {producto}\n\n📦 ¿Qué cantidad necesitas?\n• Ejemplo: '5000 unidades'"
            
            else:  # tipo_producto == "medida"
                # Verificar si ya incluye medidas
                medidas = self.detectar_medidas(mensaje)
                if medidas:
                    ancho, alto, es_cm = medidas
                    self.ancho = ancho
                    self.alto = alto
                    self.es_cm = es_cm
                    self.area, self.total = self._calcular_precio_medida(ancho, alto, es_cm)
                    self.paso = 3
                    return self._generar_cotizacion_medida()
                else:
                    self.paso = 2
                    return f"✅ Producto: {producto}\n\n📐 Indica las medidas:\n• Ejemplo: '2x3 metros' o '100x200 cm'"
        
        # ========== RESPUESTA POR DEFECTO ==========
        return "Entiendo. Escribe el producto para cotizar:\n• adhesivo, vinil, banner, tarjetas, etiquetas, volantes, etc."
    
    def _generar_menu(self) -> str:
        """Genera el menú de servicios."""
        productos = self.config.get('productos', {})
        lista = "\n".join([f"• {nombre}" for nombre in set(productos.values())][:10])
        
        return f"""📋 NUESTROS SERVICIOS - {self.config['nombre_empresa']}

{lista}

Escribe el producto para cotizar.
Ejemplo: 'tarjetas 1000 unidades' o 'adhesivo 2x3 metros'"""
    
    def _generar_precios(self) -> str:
        """Genera lista de precios."""
        return f"""💰 NUESTROS PRECIOS - {self.config['nombre_empresa']}

• Gran formato: Por cm² según acabado
• Tarjetas: Desde $75.000 por 1000 unidades
• Etiquetas: Desde $350 COP/unidad (cantidades mayores)
• Cajas: Desde $850 COP/unidad (cantidades mayores)

Para cotizar exacto, dime el producto y la cantidad/medida."""
    
    def _generar_cotizacion_cantidad(self, precio_str: str) -> str:
        """Genera la cotización para productos por cantidad."""
        return f"""📏 COTIZACIÓN - {self.producto.upper()}

   • Cantidad: {self.cantidad:,} unidades
   • Precio: {precio_str}
   • **TOTAL: ${self.total:,.0f} COP**

⏱️ Tiempo de entrega: {self.config.get('tiempos_entrega', {}).get('tarjetas', '2-3 días hábiles')}
✅ Incluye: Impresión según especificaciones

¿Confirmas el pedido? Escribe 'si' o 'no'"""
    
    def _generar_cotizacion_medida(self) -> str:
        """Genera la cotización para productos por medida."""
        if self.es_cm:
            medida_str = f"{int(self.ancho)}cm x {int(self.alto)}cm"
        else:
            medida_str = f"{self.ancho}m x {self.alto}m"
        
        return f"""📏 COTIZACIÓN - {self.producto.upper()}

   • Medidas: {medida_str}
   • Área: {self.area:.2f} m²
   • **TOTAL: ${self.total:,.0f} COP**

⏱️ Tiempo de entrega: {self.config.get('tiempos_entrega', {}).get('gran_formato', '1-3 días hábiles')}
✅ Incluye: Impresión + acabado

¿Confirmas el pedido? Escribe 'si' o 'no'"""
    
    def _generar_mensaje_personalizado(self) -> str:
        """Genera mensaje para productos personalizados."""
        return self.config.get('cotizacion_personalizada', {}).get('mensaje', 
            "Este producto requiere cotización personalizada. Por favor indícanos las especificaciones.")
    
    def _generar_confirmacion(self) -> str:
        """Genera mensaje de confirmación."""
        contacto = self.config.get('mensajes', {}).get('contacto', 
            f"📞 {self.config['telefono']}")
        
        return f"""🎉 ¡Pedido confirmado!

📋 SIGUIENTES PASOS:
   1️⃣ Te enviaremos la cotización formal
   2️⃣ Confirmas el diseño (si aplica)
   3️⃣ Pago del 50% de anticipo
   4️⃣ Producimos tu pedido
   5️⃣ Te avisamos cuando esté listo

{contacto}
⏱️ Tiempo estimado según producto

¿Tienes el diseño listo o necesitas que lo creemos?"""
    
    def _resetear_estado(self):
        """Resetea el estado para una nueva conversación."""
        self.paso = 0
        self.producto = None
        self.tipo_producto = None
        self.ancho = None
        self.alto = None
        self.cantidad = None
        self.area = None
        self.es_cm = False
        self.total = 0


# ========== PRUEBA DEL BOT ==========
if __name__ == "__main__":
    # Crear config de ejemplo si no existe
    import os
    
    if not os.path.exists('clientes/configs'):
        os.makedirs('clientes/configs')
    
    config_ejemplo = {
        "nombre_empresa": "Publiya7",
        "telefono": "+57 314 390 9874",
        "email": "publiya7@gmail.com",
        "precios": {
            "gran_formato": {
                "banner": {"cm2_con_terminado": 8.5},
                "adhesivo": {"laminado_cm2": 9.4}
            },
            "etiquetas": {
                "1000_a_3000_unid": 550,
                "desde_10000_unid": 350
            },
            "cajas": {
                "1000_a_2000_unid": 1000,
                "desde_9000_unid": 850
            }
        },
        "productos": {
            "adhesivo": "Adhesivo Laminado",
            "vinil": "Vinil",
            "banner": "Banner",
            "tarjeta": "Tarjetas de Presentación",
            "etiqueta": "Etiquetas",
            "caja": "Cajas",
            "camiseta": "Camisetas (Cotización Personalizada)"
        }
    }
    
    with open('clientes/configs/demo.json', 'w', encoding='utf-8') as f:
        json.dump(config_ejemplo, f, indent=2, ensure_ascii=False)
    
    # Probar el bot
    print("=" * 50)
    print("BOT DE IMPRENTA - MODO PRUEBA")
    print("=" * 50)
    print()
    
    bot = BotEngine("demo")
    
    # Simular conversación
    pruebas = [
        ("hola", "Saludo"),
        ("tarjetas", "Producto por cantidad"),
        ("5000 unidades", "Cantidad"),
        ("si", "Confirmar"),
    ]
    
    for mensaje, descripcion in pruebas:
        print(f"Cliente: {mensaje}")
        respuesta = bot.procesar_mensaje(mensaje)
        print(f"{respuesta}")
        print()
