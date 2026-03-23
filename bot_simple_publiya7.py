# Bot Engine - Versión simplificada para Publiya7
# Maneja correctamente los tipos de tarjetas

import json
import re

class BotEngine:
    def __init__(self, cliente_id):
        self.cliente_id = cliente_id
        with open(f'clientes/configs/{cliente_id}.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.reset()
    
    def reset(self):
        self.paso = 0
        self.producto = None
        self.tipo_producto = None
        self.tipo_tarjeta = None
        self.cantidad = None
        self.total = 0
    
    def procesar(self, mensaje):
        msg = mensaje.lower().strip()
        
        # Saludos
        if any(x in msg for x in ["hola", "buenas", "hey"]):
            return f"¡Hola! 👋 Bienvenido a {self.config['nombre_empresa']}.\n\n¿En qué puedo ayudarte? Pregúntame por tarjetas, etiquetas, volantes, banners, etc."
        
        # Contacto
        if msg in ["contacto", "telefono", "whatsapp"]:
            return f"📞 WhatsApp: {self.config['telefono']}\n📧 {self.config['email']}"
        
        # Detectar producto
        if self.paso == 0:
            if "tarjeta" in msg:
                self.producto = "Tarjetas"
                self.paso = 1
                return self._menu_tarjetas()
            elif "etiqueta" in msg:
                self.producto = "Etiquetas"
                self.paso = 2
                return "📦 ¿Qué cantidad de etiquetas necesitas?"
            elif "caja" in msg:
                self.producto = "Cajas"
                self.paso = 2
                return "📦 ¿Qué cantidad de cajas necesitas?"
            elif any(x in msg for x in ["banner", "adhesivo", "vinil"]):
                return "📐 Indica las medidas (ej: 100x200 cm)"
            else:
                return "Escribe el producto: tarjetas, etiquetas, cajas, banners, etc."
        
        # Paso 1: Seleccionar tipo de tarjeta
        if self.paso == 1:
            tipo = self._detectar_tipo_tarjeta(msg)
            if tipo:
                self.tipo_tarjeta = tipo
                self.paso = 2
                return f"✅ {tipo}\n\n📦 ¿Qué cantidad necesitas? (ej: 1000, 2000, 5000)"
            else:
                return self._menu_tarjetas()
        
        # Paso 2: Cantidad
        if self.paso == 2:
            num = re.search(r'(\d+)', msg)
            if num:
                self.cantidad = int(num.group(1))
                if self.producto == "Tarjetas":
                    self.total = self._calcular_tarjeta(self.tipo_tarjeta, self.cantidad)
                elif self.producto == "Etiquetas":
                    self.total = self._calcular_etiqueta(self.cantidad)
                elif self.producto == "Cajas":
                    self.total = self._calcular_caja(self.cantidad)
                
                self.paso = 3
                return f"📏 COTIZACIÓN\n\n• Producto: {self.producto}\n• Cantidad: {self.cantidad:,}\n• TOTAL: ${self.total:,} COP\n\n¿Confirmas? (si/no)"
            else:
                return "Indica la cantidad. Ejemplo: '1000 unidades'"
        
        # Paso 3: Confirmación
        if self.paso == 3:
            if msg in ["si", "sí"]:
                self.reset()
                return "🎉 ¡Pedido confirmado! Te contactaremos pronto."
            elif msg == "no":
                self.reset()
                return "Entendido. ¿En qué más puedo ayudarte?"
            else:
                return "¿Confirmas? Escribe 'si' o 'no'"
        
        return "No entendí. Escribe el producto que necesitas."
    
    def _menu_tarjetas(self):
        return """📋 TIPOS DE TARJETAS:

1. Sencilla Brillo UV - 1 cara: $75.000
2. Sencilla Brillo UV - 2 caras: $85.000
3. Mate - 1 cara: $119.000
4. Mate - 2 caras: $130.000
5. Mate con Reserva UV - 1 cara: $145.000
6. Mate con Reserva UV - 2 caras: $165.000
7. Estampada (Dorado/Plateado) - 1 lado: $350.000
8. Estampada - 2 lados: $380.000
9. Imanadas: $390.000

¿Qué tipo necesitas? (escribe el número o nombre)"""
    
    def _detectar_tipo_tarjeta(self, msg):
        if "1" in msg or "sencilla 1" in msg: return "Sencilla Brillo UV 1 cara"
        if "2" in msg or "sencilla 2" in msg: return "Sencilla Brillo UV 2 caras"
        if "3" in msg or "mate 1" in msg: return "Mate 1 cara"
        if "4" in msg or "mate 2" in msg: return "Mate 2 caras"
        if "5" in msg or "reserva 1" in msg: return "Mate Reserva 1 cara"
        if "6" in msg or "reserva 2" in msg: return "Mate Reserva 2 caras"
        if "7" in msg or "estampada 1" in msg: return "Estampada 1 lado"
        if "8" in msg or "estampada 2" in msg: return "Estampada 2 lados"
        if "9" in msg or "imanada" in msg or "iman" in msg: return "Imanadas"
        return None
    
    def _calcular_tarjeta(self, tipo, cantidad):
        precios = {
            "Sencilla Brillo UV 1 cara": 75000,
            "Sencilla Brillo UV 2 caras": 85000,
            "Mate 1 cara": 119000,
            "Mate 2 caras": 130000,
            "Mate Reserva 1 cara": 145000,
            "Mate Reserva 2 caras": 165000,
            "Estampada 1 lado": 350000,
            "Estampada 2 lados": 380000,
            "Imanadas": 390000
        }
        base = precios.get(tipo, 75000)
        factor = 1.0
        if cantidad >= 5000: factor = 0.85
        elif cantidad >= 3000: factor = 0.90
        elif cantidad >= 2000: factor = 0.95
        return int(base * factor * (cantidad / 1000))
    
    def _calcular_etiqueta(self, cantidad):
        if 1000 <= cantidad <= 3000: precio = 550
        elif 4000 <= cantidad <= 6000: precio = 480
        elif 7000 <= cantidad <= 9000: precio = 450
        else: precio = 350
        return cantidad * precio
    
    def _calcular_caja(self, cantidad):
        if 1000 <= cantidad <= 2000: precio = 1000
        elif 3000 <= cantidad <= 5000: precio = 950
        elif 6000 <= cantidad <= 8000: precio = 900
        else: precio = 850
        return cantidad * precio


# Prueba interactiva
if __name__ == "__main__":
    print("=" * 50)
    print("BOT PUBLIYA7 - MODO INTERACTIVO")
    print("=" * 50)
    print("Escribe 'salir' para terminar\n")
    
    bot = BotEngine("publiya7")
    
    while True:
        msg = input("Cliente: ").strip()
        if msg.lower() == "salir":
            print("\n¡Hasta luego!")
            break
        respuesta = bot.procesar(msg)
        print(f"Bot: {respuesta}\n")
