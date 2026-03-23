# Bot de Atencion al Cliente - Imprenta (Version Simplificada)
# Solo clientes directos - Precio unico
# Desarrollado por: Andres

import re

# ========== CONFIGURACION ==========
NOMBRE_EMPRESA = "Imprenta y Publicidad"
TELEFONO = "+57 XXX XXX XXXX"
EMAIL = "contacto@empresa.com"

# Precios unicos (solo clientes directos)
PRECIO_M2 = 94000        # $94.000 por metro cuadrado
PRECIO_CM2 = 9.4         # $9.4 por centimetro cuadrado

# ========== INICIO ==========
print("=" * 55)
print(f"  {NOMBRE_EMPRESA}")
print("  ATENCION AL CLIENTE")
print("=" * 55)
print("")
print("¡Hola! Bienvenido a nuestra imprenta.")
print("Te ayudamos con: avisos, vallas, tarjetas, camisetas,")
print("termos personalizados, cajas, etiquetas y mas.")
print("Escribe 'menu' para ver opciones o 'salir' para terminar.")
print("")

# Variables
paso = 0  # 0 = inicio, 1 = esperando medidas, 2 = listo para cotizar
producto = None
ancho = None
alto = None
area = None
es_cm = False

def calcular_precio(ancho_m, alto_m, es_medida_cm):
    """Calcula el precio segun medidas"""
    if es_medida_cm:
        # Medidas ya estan en cm, calcular cm2
        area_cm2 = ancho_m * alto_m * 10000  # Convertir a cm2
        total = area_cm2 * PRECIO_CM2
        area_m2 = ancho_m * alto_m
    else:
        # Medidas en metros
        area_m2 = ancho_m * alto_m
        total = area_m2 * PRECIO_M2
    return area_m2, total

while True:
    mensaje = input("Cliente: ").strip().lower()
    
    # ========== SALIR ==========
    if mensaje in ["salir", "exit", "adios", "chao"]:
        print("")
        print("¡Gracias por contactarnos! Estamos aqui para lo que necesites.")
        print(f"WhatsApp: {TELEFONO} | Email: {EMAIL}")
        break
    
    # ========== PASO 2: Mostrar cotizacion ==========
    if paso == 2:
        if mensaje in ["si", "sí", "confirmo", "ok", "dale", "perfecto"]:
            print("")
            print("Bot: 🎉 ¡Pedido confirmado!")
            print("Bot: ")
            print("Bot: 📋 SIGUIENTES PASOS:")
            print("Bot:    1️⃣  Te enviaremos la cotizacion formal")
            print("Bot:    2️⃣  Confirmas el diseño")
            print("Bot:    3️⃣  Pago del 50% de anticipo")
            print("Bot:    4️⃣  Producimos tu pedido")
            print("Bot:    5️⃣  Te avisamos cuando este listo")
            print("Bot: ")
            print(f"Bot: 📱 Te contactaremos al: {TELEFONO}")
            print("Bot: ⏱️  Tiempo: 1-3 dias habiles")
            paso = 0
            continue
        elif mensaje in ["no", "cancelar", "esperar"]:
            print("Bot: Entendido. ¿Quieres modificar algo? Escribe las nuevas medidas.")
            paso = 1
            continue
        else:
            print("Bot: ¿Confirmas el pedido? Escribe 'si' para continuar o 'no' para modificar.")
            continue
    
    # ========== PASO 1: Esperando medidas ==========
    if paso == 1:
        # Buscar medidas en cm
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|centimetros?)', mensaje)
        if match:
            cm1 = float(match.group(1))
            cm2 = float(match.group(2))
            ancho = cm1 / 100
            alto = cm2 / 100
            es_cm = True
        else:
            # Buscar en metros
            match = re.search(r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:m|metros?)?', mensaje)
            if match:
                ancho = float(match.group(1))
                alto = float(match.group(2))
                es_cm = False
        
        if ancho and alto:
            area_m2, total = calcular_precio(ancho, alto, es_cm)
            paso = 2
            
            print("")
            print(f"Bot: 📏 COTIZACION - {producto.upper()}")
            print("")
            if es_cm:
                print(f"Bot:    • Medidas: {int(ancho*100)}cm x {int(alto*100)}cm")
            else:
                print(f"Bot:    • Medidas: {ancho}m x {alto}m")
            print(f"Bot:    • Area: {area_m2:.2f} m²")
            print(f"Bot:    • Precio: ${PRECIO_M2:,}/m²")
            print(f"Bot:    • **TOTAL: ${total:,.0f} COP**")
            print("Bot: ")
            print("Bot: ⏱️  Tiempo de entrega: 1-3 dias habiles")
            print("Bot: ✅ Incluye: Impresion + laminado (mate o brillante)")
            print("Bot: ")
            print("Bot: ¿Confirmas el pedido? Escribe 'si' o 'no'")
            continue
        else:
            print("Bot: No entendi las medidas. Ejemplo: '2x3 metros' o '100x200 cm'")
            continue
    
    # ========== PASO 0: Detectar producto ==========
    # Lista de productos
    productos = {
        "adhesivo": "Adhesivo Laminado",
        "adhesivo laminado": "Adhesivo Laminado",
        "vinil": "Vinil",
        "vinilo": "Vinil",
        "banner": "Banner",
        "lona": "Lona",
        "valla": "Valla Publicitaria",
        "aviso": "Aviso",
        "pendon": "Pendon"
    }
    
    for clave, nombre in productos.items():
        if clave in mensaje:
            producto = nombre
            
            # Verificar si ya incluye medidas
            match_cm = re.search(r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|centimetros?)', mensaje)
            match_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:m|metros?)?', mensaje)
            
            if match_cm:
                cm1 = float(match_cm.group(1))
                cm2 = float(match_cm.group(2))
                ancho = cm1 / 100
                alto = cm2 / 100
                es_cm = True
                area_m2, total = calcular_precio(ancho, alto, es_cm)
                paso = 2
                
                print("")
                print(f"Bot: 📏 COTIZACION - {producto.upper()}")
                print("")
                print(f"Bot:    • Medidas: {int(ancho*100)}cm x {int(alto*100)}cm")
                print(f"Bot:    • Area: {area_m2:.2f} m²")
                print(f"Bot:    • Precio: ${PRECIO_M2:,}/m²")
                print(f"Bot:    • **TOTAL: ${total:,.0f} COP**")
                print("Bot: ")
                print("Bot: ⏱️  Tiempo: 1-3 dias habiles")
                print("Bot: ✅ Incluye: Impresion + laminado")
                print("Bot: ")
                print("Bot: ¿Confirmas? Escribe 'si' o 'no'")
                break
            elif match_m:
                ancho = float(match_m.group(1))
                alto = float(match_m.group(2))
                es_cm = False
                area_m2, total = calcular_precio(ancho, alto, es_cm)
                paso = 2
                
                print("")
                print(f"Bot: 📏 COTIZACION - {producto.upper()}")
                print("")
                print(f"Bot:    • Medidas: {ancho}m x {alto}m")
                print(f"Bot:    • Area: {area_m2:.2f} m²")
                print(f"Bot:    • Precio: ${PRECIO_M2:,}/m²")
                print(f"Bot:    • **TOTAL: ${total:,.0f} COP**")
                print("Bot: ")
                print("Bot: ⏱️  Tiempo: 1-3 dias habiles")
                print("Bot: ✅ Incluye: Impresion + laminado")
                print("Bot: ")
                print("Bot: ¿Confirmas? Escribe 'si' o 'no'")
                break
            else:
                # No tiene medidas, pedirlas
                paso = 1
                print("")
                print(f"Bot: ✅ Producto: {producto}")
                print("Bot: ")
                print("Bot: 📐 Indica las medidas:")
                print("Bot:    • Ejemplo: '2x3 metros' o '100x200 cm'")
                break
    else:
        # No encontro producto
        if paso == 0:
            if mensaje in ["menu", "opciones", "servicios"]:
                print("""Bot: 📋 NUESTROS SERVICIOS:

• GRAN FORMATO: Vinil, adhesivos, banners, lonas
• IMPRENTA: Tarjetas, volantes, afiches  
• TEXTILES: Camisetas, gorras, uniformes
• MERCHANDISING: Termos, tazas, agendas
• EMPAQUES: Cajas, etiquetas

Escribe el producto para cotizar.
Ejemplo: 'adhesivo 2x3 metros' o 'vinil 100x200 cm'""")
            elif mensaje in ["hola", "buenos dias", "buenas tardes"]:
                print(f"Bot: ¡Hola! Bienvenido a {NOMBRE_EMPRESA}. ¿En que puedo ayudarte?")
            elif mensaje in ["precio", "precios", "costo"]:
                print(f"""Bot: 💰 NUESTROS PRECIOS:

• Gran formato: ${PRECIO_M2:,} COP/m²
• Equivalente: ${PRECIO_CM2} COP/cm²

Para cotizar exacto, dime el producto y las medidas.
Ejemplo: 'adhesivo 2x3 metros'""")
            else:
                print("Bot: Entiendo. Escribe el producto para cotizar:")
                print("Bot:    • adhesivo, vinil, banner, lona, tarjetas, camisetas")

print("")
print("=" * 55)
print("  Conversacion finalizada")
print("=" * 55)
