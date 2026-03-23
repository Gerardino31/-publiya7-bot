# Bot Publiya7 - Versión Humana y Cortés
# Con saludos personalizados y tono conversacional

import json
import re
import sys
import os
from datetime import datetime
import random

# Agregar backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from database.pedidos_db import PedidosDB
from backend.services.notificador_email import NotificadorEmail

class BotPubliya7:
    def __init__(self):
        self.reset()
        self.db = PedidosDB()
        self.notificador = NotificadorEmail()
    
    def _obtener_saludo_horario(self):
        """Genera un saludo según la hora del día."""
        hora = datetime.now().hour
        
        if 6 <= hora < 12:
            saludos = [
                "¡Buenos días! ☀️ ¿Cómo está? Espero que tenga un excelente día.",
                "¡Buenos días! 🌅 Bienvenido a Publiya7. Será un gusto atenderle.",
                "¡Hola! Buenos días ☀️ ¿En qué puedo ayudarle hoy?"
            ]
        elif 12 <= hora < 18:
            saludos = [
                "¡Buenas tardes! 😊 ¿Cómo le va? Gracias por contactarnos.",
                "¡Buenas tardes! 🌤️ Bienvenido. Estoy aquí para ayudarle con su pedido.",
                "¡Hola! Buenas tardes 😊 ¿Qué necesita para su proyecto hoy?"
            ]
        else:
            saludos = [
                "¡Buenas noches! 🌙 Gracias por escribirnos. ¿Cómo puedo ayudarle?",
                "¡Buenas noches! ⭐ Bienvenido a Publiya7. Será un placer atenderle.",
                "¡Hola! Buenas noches 🌙 ¿En qué puedo asistirle esta noche?"
            ]
        
        return random.choice(saludos)
    
    def _frases_cortesia(self, tipo="general"):
        """Frases de cortesía según el contexto."""
        frases = {
            "general": [
                "Con mucho gusto le ayudo...",
                "Será un placer atenderle...",
                "Con gusto le ayudo con eso..."
            ],
            "cotizando": [
                "Permítame un momento mientras preparo su cotización...",
                "Déjeme calcular eso para usted...",
                "Un momento, por favor. Voy a prepararle la mejor opción..."
            ],
            "excelente_eleccion": [
                "¡Excelente elección! Ese producto tiene muy buena acogida.",
                "¡Muy buen gusto! Es uno de nuestros productos más solicitados.",
                "¡Perfecto! Esa es una opción muy popular entre nuestros clientes."
            ],
            "agradecimiento": [
                "Ha sido un verdadero gusto atenderle.",
                "Gracias por confiar en Publiya7.",
                "Fue un placer ayudarle con su pedido."
            ],
            "despedida": [
                "Esperamos que se haya sentido bien atendido. ¿Hay algo más en lo que pueda ayudarle?",
                "¿Cómo fue su experiencia con nosotros? Estamos aquí para cualquier otra consulta.",
                "Que tenga un excelente día. ¡Estamos a sus órdenes!"
            ]
        }
        return random.choice(frases.get(tipo, frases["general"]))
    
    def reset(self):
        self.paso = 0
        self.categoria = None
        self.tipo = None
        self.cantidad = None
        self.total = 0
        self.datos_cliente = {}  # Para guardar info del cliente
    
    def procesar(self, mensaje):
        msg = mensaje.lower().strip()
        
        # Saludos
        if any(x in msg for x in ["hola", "buenas", "hey", "saludos"]):
            saludo = self._obtener_saludo_horario()
            return f"""{saludo}

Soy su asistente virtual de **Publiya7 - Publicidad al Instante**. 🎨

{self._frases_cortesia('general')}

¿Qué producto le interesa hoy? Puede elegir una categoría:

1️⃣ Tarjetas de Presentación
2️⃣ Volantes y Plegables  
3️⃣ Etiquetas
4️⃣ Cajas
5️⃣ Gran Formato (Banners, Adhesivos, etc.)
6️⃣ Sellos
7️⃣ Otros productos

*Escriba el número o nombre de la categoría que necesite.*"""
        
        # Contacto
        if msg in ["contacto", "telefono", "whatsapp", "email"]:
            return f"""{self._frases_cortesia('general')}

Aquí tiene nuestra información de contacto:

📞 **WhatsApp:** +57 314 390 9874 / +57 323 360 5163
📧 **Email:** publiya7@gmail.com
📍 **Ubicación:** Medellín, Colombia
🕐 **Horario:** Lunes a Viernes 8am-5pm, Sábados 8am-2pm

Síganos en Instagram **@publiya7** para ver nuestros trabajos. {self._frases_cortesia('agradecimiento')}"""
        
        # PASO 0: Seleccionar categoría
        if self.paso == 0:
            if any(x in msg for x in ["1", "tarjeta"]):
                self.categoria = "tarjetas"
                return self._menu_tarjetas()
            elif any(x in msg for x in ["2", "volante", "plegable", "flyer"]):
                self.categoria = "volantes"
                return self._menu_volantes()
            elif any(x in msg for x in ["3", "etiqueta"]):
                self.categoria = "etiquetas"
                return self._menu_etiquetas()
            elif any(x in msg for x in ["4", "caja"]):
                self.categoria = "cajas"
                return self._menu_cajas()
            elif any(x in msg for x in ["5", "gran formato", "banner", "adhesivo", "vinil", "panaflex"]):
                self.categoria = "gran_formato"
                return self._menu_gran_formato()
            elif any(x in msg for x in ["6", "sello"]):
                self.categoria = "sellos"
                return self._menu_sellos()
            elif any(x in msg for x in ["7", "otros", "talonario", "afiche", "bastidor", "tijera", "aviso", "carnet", "pad", "souvenir", "termo", "cascara", "plotter"]):
                self.categoria = "otros"
                return self._menu_otros()
            else:
                return f"Disculpe, no pude identificar esa categoría. {self._frases_cortesia('general')}\n\n¿Podría elegir una opción del 1 al 7, o escribirme el nombre del producto que necesita?"
        
        # PASO 1: Seleccionar tipo
        if self.paso == 1:
            resultado = self._procesar_tipo(msg)
            if "Disculpe" not in resultado:
                return resultado
            return resultado
        
        # PASO 2: Cantidad o Medidas
        if self.paso == 2:
            # Gran formato necesita medidas, no cantidad
            if self.categoria == "gran_formato":
                medidas = re.search(r'(\d+)\s*x\s*(\d+)', msg)
                if medidas:
                    ancho = int(medidas.group(1))
                    alto = int(medidas.group(2))
                    self.cantidad = f"{ancho}x{alto}cm"
                    area_cm2 = ancho * alto
                    self.total = self._calcular_precio_gran_formato(area_cm2)
                    self.paso = 3
                    return self._generar_cotizacion_gran_formato(area_cm2)
                else:
                    return f"Disculpe, necesito las medidas para calcularle el precio. {self._frases_cortesia('general')}\n\n¿Podría indicarme las medidas en formato ancho x alto? Por ejemplo: **100x200** o **150x300** (en centímetros)."
            
            # Otros productos necesitan cantidad
            num = re.search(r'(\d+)', msg)
            if num:
                self.cantidad = int(num.group(1))
                self.total = self._calcular_precio()
                self.paso = 3
                return self._generar_cotizacion()
            else:
                return f"Disculpe, necesito saber la cantidad. {self._frases_cortesia('general')}\n\n¿Podría indicarme cuántas unidades necesita? Por ejemplo: **1000**, **5000**, **10000**"
        
        # PASO 3: Confirmación
        if self.paso == 3:
            if msg in ["si", "sí"]:
                # Guardar pedido en base de datos
                try:
                    numero_orden = self.db.guardar_pedido(
                        cliente_id="publiya7",
                        producto=self.categoria,
                        tipo=self.tipo,
                        cantidad=str(self.cantidad),
                        precio_total=self.total,
                        notas=f"Pedido generado por bot"
                    )
                    
                    # Preparar datos para notificación
                    pedido_data = {
                        'numero_orden': numero_orden,
                        'producto': self.tipo or self.categoria,
                        'tipo': self.tipo,
                        'cantidad': str(self.cantidad),
                        'precio_total': self.total,
                        'notas': 'Pedido generado automáticamente'
                    }
                    
                    # Enviar notificación por email
                    self.notificador.enviar_notificacion_pedido(pedido_data)
                    
                    self.reset()
                    return f"""🎉 ¡Pedido confirmado con éxito!

📋 **Número de Orden:** {numero_orden}
💰 **Total:** ${pedido_data['precio_total']:,} COP

{self._frases_cortesia('agradecimiento')}

En breve nos comunicaremos con usted al WhatsApp **+57 314 390 9874** para coordinar todos los detalles del diseño y pago.

📧 También hemos enviado un resumen completo a **publiya7@gmail.com**

{self._frases_cortesia('despedida')}

¡Que tenga un excelente día! 🌟"""
                    
                except Exception as e:
                    print(f"Error al guardar pedido: {e}")
                    self.reset()
                    return "🎉 ¡Pedido confirmado! Te contactaremos del WhatsApp +57 314 390 9874."
                    
            elif msg == "no":
                self.reset()
                return f"Entendido, no hay problema. {self._frases_cortesia('general')}\n\n¿Hay algún otro producto que le interese consultar? Estoy aquí para ayudarle."
            else:
                return f"Disculpe, necesito confirmar si desea proceder con el pedido. {self._frases_cortesia('general')}\n\n¿Le parece bien la cotización? Por favor escríbame **'sí'** para confirmar o **'no'** si prefiere revisar otras opciones."
        
        return f"Disculpe, no pude entender completamente. {self._frases_cortesia('general')}\n\n¿Podría escribir **'hola'** para comenzar de nuevo? Estaré encantado de atenderle."
    
    # ========== MENÚS DE CATEGORÍAS ==========
    
    def _menu_tarjetas(self):
        self.paso = 1
        return """📋 TARJETAS DE PRESENTACIÓN (1000 unidades)

1. Sencilla Brillo UV - 1 cara: $75.000
2. Sencilla Brillo UV - 2 caras: $85.000
3. Mate - 1 cara: $119.000
4. Mate - 2 caras: $130.000
5. Mate con Reserva UV - 1 cara: $145.000
6. Mate con Reserva UV - 2 caras: $165.000
7. Estampada (Dorado/Plateado) - 1 lado: $350.000
8. Estampada - 2 lados: $380.000
9. Imanadas: $390.000

¿Qué tipo necesitas? (1-9)"""
    
    def _menu_volantes(self):
        self.paso = 1
        return """📋 VOLANTES Y PLEGABLES

VOLANTES (1000 unidades):
1. 1 cara 13x7cm: $75.000
2. 2 caras 13x7cm: $120.000
3. 1 cara 21x10cm: $130.000
4. 2 caras 21x10cm: $220.000
5. 2 caras 21x12cm: $240.000
6. 1 cara 21x13cm: $185.000
7. 2 caras 21x13cm: $260.000

PLEGABLES (1000 unidades):
8. Tamaño Carta: $540.000
9. Tamaño Oficio: $590.000

¿Qué tipo necesitas? (1-9)"""
    
    def _menu_etiquetas(self):
        self.paso = 1
        return """📋 ETIQUETAS - Selecciona el rango:

1. 1.000 a 3.000 unidades: $550 c/u
2. 4.000 a 6.000 unidades: $480 c/u
3. 7.000 a 9.000 unidades: $450 c/u
4. Desde 10.000 unidades: $350 c/u

¿Qué rango necesitas? (1-4)"""
    
    def _menu_cajas(self):
        self.paso = 1
        return """📋 CAJAS - Selecciona el rango:

1. 1.000 a 2.000 unidades: $1.000 c/u
2. 3.000 a 5.000 unidades: $950 c/u
3. 6.000 a 8.000 unidades: $900 c/u
4. Más de 9.000 unidades: $850 c/u

¿Qué rango necesitas? (1-4)"""
    
    def _menu_gran_formato(self):
        self.paso = 1
        return """📋 GRAN FORMATO (Precio por cm²)

1. Banner con terminado: $8.5/cm²
2. Banner sin terminado: $7.5/cm²
3. Panaflex: $10/cm²
4. Adhesivo sin laminar: $7.5/cm²
5. Adhesivo laminado: $9.4/cm²
6. Adhesivo laminado con contorno: $12/cm²
7. Microperforado: $10/cm²
8. Vinilos decorativos: $9.4/cm²

¿Qué tipo necesitas? (1-8)

Luego indicarás las medidas (ej: 100x200 cm)"""
    
    def _menu_sellos(self):
        self.paso = 1
        return """📋 SELLOS AUTOMÁTICOS

1. 10x26mm: $48.000
2. 14x38mm: $50.000
3. 18x47mm: $65.000
4. 22x58mm: $75.000
5. 27x65mm: $85.000
6. 25x70mm: $95.000

¿Qué tamaño necesitas? (1-6)"""
    
    def _menu_otros(self):
        self.paso = 1
        return """📋 OTROS PRODUCTOS

1. Talonarios (papel natural o químico)
2. Afiches (1000 unidades)
3. Bastidores (por cm²)
4. Tijeras publicitarias
5. Avisos luminosos
6. Carnets PVC
7. Pad Mouse
8. Cáscara de huevo (1000-2000 unid)
9. Plotter de corte
10. Souvenirs (Tulas, Termos)

¿Qué producto necesitas? (1-10)"""
    
    # ========== PROCESAR TIPO SELECCIONADO ==========
    
    def _procesar_tipo(self, msg):
        try:
            opcion = int(re.search(r'(\d+)', msg).group(1))
        except:
            return f"Disculpe, no pude entender su selección. {self._frases_cortesia('general')}\n\n¿Podría indicarme el número de la opción que prefiere?"
        
        # Guardar tipo seleccionado
        if self.categoria == "tarjetas":
            tipos = ["Sencilla Brillo UV 1 cara", "Sencilla Brillo UV 2 caras", "Mate 1 cara", 
                    "Mate 2 caras", "Mate Reserva 1 cara", "Mate Reserva 2 caras",
                    "Estampada 1 lado", "Estampada 2 lados", "Imanadas"]
            if 1 <= opcion <= 9:
                self.tipo = tipos[opcion-1]
        
        elif self.categoria == "volantes":
            if 1 <= opcion <= 9:
                self.tipo = f"Volante/Plegable opción {opcion}"
        
        elif self.categoria == "etiquetas":
            rangos = ["1000-3000", "4000-6000", "7000-9000", "10000+"]
            if 1 <= opcion <= 4:
                self.tipo = rangos[opcion-1]
        
        elif self.categoria == "cajas":
            rangos = ["1000-2000", "3000-5000", "6000-8000", "9000+"]
            if 1 <= opcion <= 4:
                self.tipo = rangos[opcion-1]
        
        elif self.categoria == "gran_formato":
            tipos = ["Banner con terminado", "Banner sin terminado", "Panaflex",
                    "Adhesivo sin laminar", "Adhesivo laminado", "Adhesivo con contorno",
                    "Microperforado", "Vinilos decorativos"]
            if 1 <= opcion <= 8:
                self.tipo = tipos[opcion-1]
        
        elif self.categoria == "sellos":
            if 1 <= opcion <= 6:
                self.tipo = f"Sello {opcion}"
        
        elif self.categoria == "otros":
            self.tipo = f"Producto {opcion}"
        
        if not self.tipo:
            return "Disculpe, no pude entender su selección. ¿Podría indicarme el número de la opción que prefiere?"
        
        self.paso = 2
        
        # Mensaje diferente según categoría
        if self.categoria == "gran_formato":
            return f"✅ {self.tipo}\n\n{self._frases_cortesia('excelente_eleccion')}\n\n📐 ¿Podría indicarme las medidas que necesita? (Por ejemplo: 100x200, 150x300) en centímetros."
        elif self.categoria == "sellos":
            return f"✅ {self.tipo}\n\n{self._frases_cortesia('excelente_eleccion')}\n\n📦 ¿Cuántos sellos necesita? (Puede ser 1, 2, 5 o los que requiera)"
        else:
            return f"✅ {self.tipo}\n\n{self._frases_cortesia('excelente_eleccion')}\n\n📦 ¿Qué cantidad necesita? (Por ejemplo: 1000, 5000, 10000 unidades)"
    
    def _calcular_precio_gran_formato(self, area_cm2):
        """Calcula precio para gran formato por cm²."""
        precios_cm2 = {
            "Banner con terminado": 8.5,
            "Banner sin terminado": 7.5,
            "Panaflex": 10,
            "Adhesivo sin laminar": 7.5,
            "Adhesivo laminado": 9.4,
            "Adhesivo laminado con contorno": 12,
            "Microperforado": 10,
            "Vinilos decorativos": 9.4
        }
        precio = precios_cm2.get(self.tipo, 9.4)
        return int(area_cm2 * precio)
    
    def _generar_cotizacion_gran_formato(self, area_cm2):
        """Genera cotización para gran formato."""
        precios_cm2 = {
            "Banner con terminado": 8.5,
            "Banner sin terminado": 7.5,
            "Panaflex": 10,
            "Adhesivo sin laminar": 7.5,
            "Adhesivo laminado": 9.4,
            "Adhesivo laminado con contorno": 12,
            "Microperforado": 10,
            "Vinilos decorativos": 9.4
        }
        precio_cm2 = precios_cm2.get(self.tipo, 9.4)
        
        return f"""📏 **COTIZACIÓN PREPARADA - GRAN FORMATO**

{self._frases_cortesia('cotizando')}

• **Producto:** {self.tipo}
• **Medidas:** {self.cantidad}
• **Área total:** {area_cm2:,} cm²
• **Precio por cm²:** ${precio_cm2}
• **Inversión total:** ${self.total:,} COP

⏱️ **Tiempo de entrega:** 2-3 días hábiles
✅ **Incluye:** Impresión de alta calidad y acabado profesional

¿Le parece bien esta cotización? Confírmeme con un **"sí"** y gestionamos su pedido de inmediato."""
    
    # ========== CALCULAR PRECIO ==========
    
    def _calcular_precio(self):
        cant = self.cantidad
        
        # Tarjetas
        if self.categoria == "tarjetas":
            precios = {
                "Sencilla Brillo UV 1 cara": 75000, "Sencilla Brillo UV 2 caras": 85000,
                "Mate 1 cara": 119000, "Mate 2 caras": 130000,
                "Mate Reserva 1 cara": 145000, "Mate Reserva 2 caras": 165000,
                "Estampada 1 lado": 350000, "Estampada 2 lados": 380000, "Imanadas": 390000
            }
            base = precios.get(self.tipo, 75000)
            factor = 0.85 if cant >= 5000 else 0.90 if cant >= 3000 else 0.95 if cant >= 2000 else 1.0
            return int(base * factor * (cant / 1000))
        
        # Etiquetas
        elif self.categoria == "etiquetas":
            if self.tipo == "1000-3000": precio = 550
            elif self.tipo == "4000-6000": precio = 480
            elif self.tipo == "7000-9000": precio = 450
            else: precio = 350
            return cant * precio
        
        # Cajas
        elif self.categoria == "cajas":
            if self.tipo == "1000-2000": precio = 1000
            elif self.tipo == "3000-5000": precio = 950
            elif self.tipo == "6000-8000": precio = 900
            else: precio = 850
            return cant * precio
        
        # Volantes
        elif self.categoria == "volantes":
            precios_base = {1: 75000, 2: 120000, 3: 130000, 4: 220000, 5: 240000, 
                          6: 185000, 7: 260000, 8: 540000, 9: 590000}
            base = precios_base.get(int(self.tipo.split()[-1]), 75000)
            return int(base * (cant / 1000))
        
        # Sellos
        elif self.categoria == "sellos":
            precios = {1: 48000, 2: 50000, 3: 65000, 4: 75000, 5: 85000, 6: 95000}
            precio_unitario = precios.get(int(self.tipo.split()[-1]), 48000)
            return precio_unitario * cant  # Multiplicar por cantidad
        
        # Gran formato (necesitaría medidas, simplificado)
        elif self.categoria == "gran_formato":
            return 0  # Cotización manual
        
        # Otros
        return 0
    
    # ========== GENERAR COTIZACIÓN ==========
    
    def _generar_cotizacion(self):
        if self.total == 0:
            return f"✅ {self.tipo}\n\nEste producto requiere una cotización personalizada. {self._frases_cortesia('general')}\n\n📞 Puede contactarnos al WhatsApp: +57 314 390 9874\nCon gusto le atenderemos personalmente."
        
        # Texto según categoría
        if self.categoria == "sellos":
            cantidad_str = f"{self.cantidad} sello{'s' if self.cantidad > 1 else ''}"
        else:
            cantidad_str = f"{self.cantidad:,} unidades"
        
        return f"""📏 **COTIZACIÓN PREPARADA**

{self._frases_cortesia('cotizando')}

• **Producto:** {self.tipo}
• **Cantidad:** {cantidad_str}
• **Inversión total:** ${self.total:,} COP

⏱️ **Tiempo de entrega:** 2-5 días hábiles
✅ **Incluye:** Impresión de alta calidad según especificaciones

¿Le parece bien esta cotización? Confírmeme con un **"sí"** y gestionamos su pedido de inmediato."""


# ========== EJECUCIÓN INTERACTIVA ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PUBLIYA7 - BOT INTERACTIVO v2.0")
    print("=" * 60)
    print("Escribe 'salir' para terminar\n")
    
    bot = BotPubliya7()
    
    while True:
        try:
            msg = input("Cliente: ").strip()
            if msg.lower() == "salir":
                print("\n¡Hasta luego! 👋")
                break
            
            respuesta = bot.procesar(msg)
            print(f"\nBot: {respuesta}\n")
            
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego! 👋")
            break
