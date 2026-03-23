# Bot de Atencion al Cliente - Imprenta y Publicidad
# Version 2.1 - Corregido
# Cliente: [Nombre de la empresa]
# Desarrollado por: Andres

print("=" * 55)
print("  IMPRENTA Y PUBLICIDAD - ATENCION AL CLIENTE")
print("=" * 55)
print("")
print("Hola! Bienvenido a nuestra imprenta.")
print("Te ayudamos con: avisos, vallas, tarjetas, camisetas,")
print("termos personalizados, cajas, etiquetas y mas.")
print("Escribe 'menu' para ver opciones o 'salir' para terminar.")
print("")

# Variables de estado
paso_cotizacion = 0  # 0 = nada, 1 = esperando medidas, 2 = esperando tipo cliente
producto_actual = None
ancho_actual = None
alto_actual = None
area_actual = None
es_cm_actual = False

# Precios
PRECIO_DIRECTO_M2 = 94000
PRECIO_TERCERO_M2 = 47000

import re

while True:
    mensaje = input("Cliente: ").strip()
    msg = mensaje.lower()
    
    # ========== SALIR ==========
    if msg in ["salir", "exit", "adios", "chao", "hasta luego"]:
        print("")
        print("Gracias por contactarnos! Estamos aqui para lo que necesites.")
        print("WhatsApp: +57 XXX XXX XXXX | Email: contacto@empresa.com")
        break
    
    # ========== PASO 2: Esperando tipo de cliente ==========
    if paso_cotizacion == 2:
        if any(p in msg for p in ["si", "sí", "si soy", "claro", "tercero", "agencia", "soy agencia", "revendedor", "diseñador", "disenador", "imprenta"]):
            # Es tercero - solicitar documentos
            print("")
            print("Bot: Perfecto, eres agencia publicitaria/tercero.")
            print("Bot: Para aplicar el precio especial de $47.000/m², necesito:")
            print("Bot:    📄 RUT de la empresa")
            print("Bot:    📄 Cámara de Comercio (vigente)")
            print("Bot:    📄 Tarjeta profesional (si aplica)")
            print("Bot: ")
            print("Bot: Puedes enviarlos a: documentos@empresa.com o WhatsApp: +57 XXX XXX XXXX")
            print("Bot: Una vez verificados, te envio la cotizacion formal.")
            print("")
            print(f"Bot: 📏 Tu cotizacion: {area_actual:.2f} m² = **${area_actual * PRECIO_TERCERO_M2:,.0f} COP**")
            print("Bot: ")
            print("Bot: ¿Tienes los documentos listos para enviarlos?")
            paso_cotizacion = 0
            continue
            
        elif any(p in msg for p in ["no", "no soy", "cliente directo", "directo", "soy directo", "para mi", "mi negocio", "mi empresa", "personal"]):
            # Es cliente directo - mostrar precio final
            print("")
            print("Bot: Perfecto! Precio de cliente directo.")
            print("")
            print(f"Bot: 📏 COTIZACION FINAL:")
            if es_cm_actual:
                print(f"Bot:    • Medidas: {int(ancho_actual * 100)}cm x {int(alto_actual * 100)}cm")
            else:
                print(f"Bot:    • Medidas: {ancho_actual}m x {alto_actual}m")
            print(f"Bot:    • Area: {area_actual:.2f} m²")
            print(f"Bot:    • Precio: $94.000/m²")
            print(f"Bot:    • **TOTAL: ${area_actual * PRECIO_DIRECTO_M2:,.0f} COP**")
            print("Bot: ")
            print("Bot: ⏱️ Tiempo de entrega: 1-3 dias habiles")
            print("Bot: ✅ Incluye: Impresion + laminado (mate o brillante)")
            print("Bot: ")
            print("Bot: ¿Te parece bien? Escribe 'si' para confirmar el pedido.")
            paso_cotizacion = 0
            continue
        else:
            print("Bot: Por favor responde 'si' si eres agencia/tercero, o 'no' si eres cliente directo.")
            continue
    
    # ========== PASO 1: Esperando medidas ==========
    if paso_cotizacion == 1:
        # Detectar medidas en el mensaje
        medidas_encontradas = None
        es_cm = False
        
        # Primero buscar patrones con CM (sin espacio tambien): "100x200cm", "100 x 200 cm"
        patron_cm = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|cms?|centimetros?)'
        match = re.search(patron_cm, msg)
        if match:
            # Convertir cm a metros dividiendo entre 100
            cm1 = float(match.group(1))
            cm2 = float(match.group(2))
            medidas_encontradas = (cm1 / 100.0, cm2 / 100.0)
            es_cm = True
        
        # Si no encontro en cm, buscar en metros
        if not medidas_encontradas:
            patron_metros = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:metros?|m)?'
            match = re.search(patron_metros, msg)
            if match:
                medidas_encontradas = (float(match.group(1)), float(match.group(2)))
                es_cm = False
        
        if medidas_encontradas:
            ancho_actual, alto_actual = medidas_encontradas
            es_cm_actual = es_cm
            area_actual = ancho_actual * alto_actual
            
            # Pasar al paso 2: preguntar tipo de cliente
            paso_cotizacion = 2
            print("")
            if es_cm:
                print(f"Bot: ✅ Medidas registradas: {int(ancho_actual * 100)}cm x {int(alto_actual * 100)}cm = {area_actual:.2f} m²")
            else:
                print(f"Bot: ✅ Medidas registradas: {ancho_actual}m x {alto_actual}m = {area_actual:.2f} m²")
            print("")
            print("Bot: ¿Eres agencia publicitaria o tercero?")
            print("Bot:    • Escribe 'SI' si eres: agencia, diseñador, revendedor, imprenta")
            print("Bot:    • Escribe 'NO' si eres: cliente directo (uso propio)")
            continue
        else:
            print("Bot: No entendi las medidas. Por favor escribe como: '2x3 metros' o '100x200 cm'")
            continue
    
    # ========== PASO 0: Detectar producto para iniciar cotizacion ==========
    # Detectar si menciona producto de gran formato
    if any(p in msg for p in ["adhesivo", "adhesivo laminado", "vinil", "vinilo", "banner", "lona", "pendon", "valla", "aviso", "gran formato", "fotomural", "foto mural", "afiche", "impresion gran formato"]):
        # Extraer el nombre del producto
        if "adhesivo" in msg:
            producto_actual = "Adhesivo Laminado"
        elif "vinil" in msg or "vinilo" in msg:
            producto_actual = "Vinil"
        elif "banner" in msg:
            producto_actual = "Banner"
        elif "lona" in msg:
            producto_actual = "Lona"
        elif "fotomural" in msg or "foto mural" in msg:
            producto_actual = "Fotomural"
        elif "afiche" in msg:
            producto_actual = "Afiche"
        else:
            producto_actual = "Gran Formato"
        
        # Verificar si ya incluye medidas en el mismo mensaje
        medidas_encontradas = None
        es_cm = False
        
        # Primero buscar cm (sin espacio tambien)
        patron_cm = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|cms?|centimetros?)'
        match = re.search(patron_cm, msg)
        if match:
            cm1 = float(match.group(1))
            cm2 = float(match.group(2))
            medidas_encontradas = (cm1 / 100.0, cm2 / 100.0)
            es_cm = True
        
        # Si no encontro en cm, buscar en metros
        if not medidas_encontradas:
            patron_metros = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:metros?|m)?'
            match = re.search(patron_metros, msg)
            if match:
                medidas_encontradas = (float(match.group(1)), float(match.group(2)))
                es_cm = False
        
        if medidas_encontradas:
            # Ya tiene medidas, pasar directo a preguntar tipo de cliente
            ancho_actual, alto_actual = medidas_encontradas
            es_cm_actual = es_cm
            area_actual = ancho_actual * alto_actual
            paso_cotizacion = 2
            
            print("")
            print(f"Bot: Producto: {producto_actual}")
            if es_cm:
                print(f"Bot: Medidas: {int(ancho_actual * 100)}cm x {int(alto_actual * 100)}cm = {area_actual:.2f} m²")
            else:
                print(f"Bot: Medidas: {ancho_actual}m x {alto_actual}m = {area_actual:.2f} m²")
            print("")
            print("Bot: ¿Eres agencia publicitaria o tercero?")
            print("Bot:    • Escribe 'SI' si eres: agencia, diseñador, revendedor, imprenta")
            print("Bot:    • Escribe 'NO' si eres: cliente directo (uso propio)")
            continue
        else:
            # No tiene medidas, preguntarlas
            paso_cotizacion = 1
            print("")
            print(f"Bot: ✅ Producto seleccionado: {producto_actual}")
            print("Bot: ")
            print("Bot: 📐 Por favor indica las medidas:")
            print("Bot:    • Ejemplo: '2x3 metros' o '2.5 x 1.8 m'")
            print("Bot:    • O en cm: '100x200 cm'")
            continue
    
    # ========== SALUDOS ==========
    if any(p in msg for p in ["hola", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos"]):
        print("Bot: ¡Hola! Bienvenido a nuestra imprenta. ¿En que puedo ayudarte? Escribe 'menu' para ver opciones.")
        continue
    
    # ========== MENU ==========
    if any(p in msg for p in ["menu", "opciones", "servicios", "que venden", "ayuda"]):
        print("""Bot: 📋 NUESTROS SERVICIOS:

1. GRAN FORMATO: Vinil, adhesivos, banners, lonas
2. IMPRENTA: Tarjetas, volantes, afiches
3. TEXTILES: Camisetas, gorras, uniformes
4. MERCHANDISING: Termos, tazas, agendas
5. EMPAQUES: Cajas, etiquetas

Escribe el servicio para mas informacion.
Para cotizar gran formato, escribe: 'adhesivo', 'vinil', 'banner', etc.""")
        continue
    
    # ========== PRECIOS GRAN FORMATO (sin medidas) ==========
    if any(p in msg for p in ["precio adhesivo", "precio vinil", "precio banner", "cuanto cuesta el m2", "precio metro cuadrado"]):
        print("""Bot: 💰 PRECIOS GRAN FORMATO:

• Cliente directo: $94.000 COP/m²
• Agencias/Terceros: $47.000 COP/m² (con documentacion)

Requiere:
• Cliente directo: Sin documentos adicionales
• Terceros: RUT + Cámara de Comercio

Para cotizar exacto, dime las medidas. Ejemplo: 'necesito adhesivo de 2x3 metros'""")
        continue
    
    # ========== RESPUESTA POR DEFECTO ==========
    print("Bot: Entiendo. Para ayudarte mejor:")
    print("Bot:    • Escribe 'menu' para ver servicios")
    print("Bot:    • Escribe el producto: 'adhesivo', 'vinil', 'banner', 'tarjetas'")
    print("Bot:    • O dime: 'necesito cotizar [producto] de [medidas]'")

print("")
print("=" * 55)
print("  Conversacion finalizada. ¡Vuelve pronto!")
print("=" * 55)
