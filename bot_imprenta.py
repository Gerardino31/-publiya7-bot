# Bot de Atencion al Cliente - Imprenta y Publicidad
# Version 3.0 - Con configuracion por cliente
# Lee precios desde config.json

import json
import re

# ========== CARGAR CONFIGURACION ==========
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"✅ Configuracion cargada: {config['nombre_empresa']}")
except FileNotFoundError:
    print("❌ Error: No se encontro config.json")
    print("Creando archivo de configuracion de ejemplo...")
    config = {
        "nombre_empresa": "Mi Imprenta",
        "telefono": "+57 300 000 0000",
        "precios_gran_formato": {
            "cliente_directo_m2": 94000,
            "tercero_m2": 47000
        }
    }

# Extraer variables de configuracion
NOMBRE_EMPRESA = config.get('nombre_empresa', 'Imprenta')
TELEFONO = config.get('telefono', '')
EMAIL = config.get('email', '')
CIUDAD = config.get('ciudad', '')
HORARIO = config.get('horario_atencion', '')

# Precios gran formato
PRECIO_DIRECTO_M2 = config['precios_gran_formato'].get('cliente_directo_m2', 94000)
PRECIO_TERCERO_M2 = config['precios_gran_formato'].get('tercero_m2', 47000)
PRECIO_CM2_TERCERO = config['precios_gran_formato'].get('precio_cm2_tercero', 4.7)

# Productos
PRODUCTOS = config.get('productos', {})

# Mensajes
MENSAJES = config.get('mensajes', {})

# ========== INICIO DEL BOT ==========
print("=" * 60)
print(f"  {NOMBRE_EMPRESA}")
print("  ATENCION AL CLIENTE VIRTUAL")
print("=" * 60)
print("")
print(MENSAJES.get('bienvenida', 'Hola! Bienvenido a nuestra imprenta.'))
print("Escribe 'menu' para ver opciones o 'salir' para terminar.")
print("")

# Variables de estado
paso_cotizacion = 0
producto_actual = None
ancho_actual = None
alto_actual = None
area_actual = None
es_cm_actual = False

while True:
    mensaje = input("Cliente: ").strip()
    msg = mensaje.lower()
    
    # ========== SALIR ==========
    if msg in ["salir", "exit", "adios", "chao", "hasta luego"]:
        print("")
        print(MENSAJES.get('despedida', 'Gracias por contactarnos.'))
        print(f"WhatsApp: {TELEFONO} | Email: {EMAIL}")
        break
    
    # ========== DETECTAR MEDIDAS SOLAS (sin producto) ==========
    # Esto va primero para capturar medidas en cualquier mensaje
    medidas_solas = None
    es_cm_solas = False
    
    # Buscar cm
    patron_cm = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|cms?|centimetros?)'
    match = re.search(patron_cm, msg)
    if match:
        cm1 = float(match.group(1))
        cm2 = float(match.group(2))
        medidas_solas = (cm1 / 100.0, cm2 / 100.0)
        es_cm_solas = True
    
    # Buscar metros
    if not medidas_solas:
        patron_metros = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:metros?|m)?'
        match = re.search(patron_metros, msg)
        if match:
            medidas_solas = (float(match.group(1)), float(match.group(2)))
            es_cm_solas = False
    
    # Si hay medidas pero NO hay producto de gran formato, preguntar producto
    if medidas_solas and not any(p in msg for p in ["adhesivo", "vinil", "vinilo", "banner", "lona", "pendon", "valla", "aviso", "gran formato", "fotomural", "afiche"]):
        ancho_actual, alto_actual = medidas_solas
        es_cm_actual = es_cm_solas
        area_actual = ancho_actual * alto_actual
        paso_cotizacion = 2  # Esperando tipo cliente (pero primero necesitamos producto)
        
        print("")
        if es_cm_solas:
            print(f"Bot: ✅ Medidas: {int(ancho_actual * 100)}cm x {int(alto_actual * 100)}cm = {area_actual:.2f} m²")
        else:
            print(f"Bot: ✅ Medidas: {ancho_actual}m x {alto_actual}m = {area_actual:.2f} m²")
        print("")
        print("Bot: ¿Que producto necesitas para estas medidas?")
        print("Bot:    • Vinil adhesivo")
        print("Bot:    • Adhesivo laminado")
        print("Bot:    • Banner")
        print("Bot:    • Lona")
        continue
    
    # ========== PASO 2: Tenemos medidas, esperando producto y tipo cliente ==========
    if paso_cotizacion == 2:
        # Primero verificar si el cliente está diciendo el producto AHORA
        if producto_actual is None:
            if any(p in msg for p in ["vinil", "vinilo", "adhesivo", "adhesivo laminado", "banner", "lona", "pendon", "valla", "aviso"]):
                # Guardar el producto
                if "adhesivo" in msg:
                    producto_actual = "Adhesivo Laminado"
                elif "vinil" in msg:
                    producto_actual = "Vinil"
                elif "banner" in msg:
                    producto_actual = "Banner"
                elif "lona" in msg:
                    producto_actual = "Lona"
                else:
                    producto_actual = "Gran Formato"
                # Continuar al flujo de tipo de cliente
            else:
                # Todavia no ha dicho el producto
                print("Bot: Por favor indica el producto: vinil, adhesivo, banner o lona")
                continue
        
        # Ahora verificar tipo de cliente
        if any(p in msg for p in ["si", "sí", "si soy", "claro", "tercero", "agencia", "soy agencia", "revendedor", "diseñador", "disenador", "imprenta"]):
            # Es tercero - solicitar documentos
            print("")
            print("Bot: Perfecto, eres agencia publicitaria/tercero.")
            print(f"Bot: {MENSAJES.get('solicitar_documentos_tercero', 'Para precios de tercero, necesitamos documentacion.')}")
            print("Bot:    📄 RUT de la empresa")
            print("Bot:    📄 Cámara de Comercio (vigente)")
            print("Bot: ")
            print(f"Bot: Puedes enviarlos a: {EMAIL} o WhatsApp: {TELEFONO}")
            print("")
            print(f"Bot: 📏 Tu cotizacion: {area_actual:.2f} m² = **${area_actual * PRECIO_TERCERO_M2:,.0f} COP**")
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
            print(f"Bot:    • Precio: ${PRECIO_DIRECTO_M2:,.0f}/m²")
            print(f"Bot:    • **TOTAL: ${area_actual * PRECIO_DIRECTO_M2:,.0f} COP**")
            print("Bot: ")
            print(f"Bot: ⏱️ {config.get('tiempo_entrega_gran_formato', '1-3 días hábiles')}")
            print("Bot: ✅ Incluye: Impresion + laminado (mate o brillante)")
            print("Bot: ")
            print("Bot: ¿Te parece bien? Escribe 'si' para confirmar.")
            paso_cotizacion = 0
            continue
        else:
            print("Bot: Por favor responde 'si' si eres agencia/tercero, o 'no' si eres cliente directo.")
            continue
    
    # ========== PASO 1: Esperando medidas ==========
    if paso_cotizacion == 1:
        medidas_encontradas = None
        es_cm = False
        
        # Buscar cm
        patron_cm = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|cms?|centimetros?)'
        match = re.search(patron_cm, msg)
        if match:
            cm1 = float(match.group(1))
            cm2 = float(match.group(2))
            medidas_encontradas = (cm1 / 100.0, cm2 / 100.0)
            es_cm = True
        
        # Buscar metros
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
            paso_cotizacion = 2
            
            print("")
            if es_cm:
                print(f"Bot: ✅ Medidas: {int(ancho_actual * 100)}cm x {int(alto_actual * 100)}cm = {area_actual:.2f} m²")
            else:
                print(f"Bot: ✅ Medidas: {ancho_actual}m x {alto_actual}m = {area_actual:.2f} m²")
            print("")
            print("Bot: ¿Eres agencia publicitaria o tercero?")
            print("Bot:    • Escribe 'SI' si eres: agencia, diseñador, revendedor")
            print("Bot:    • Escribe 'NO' si eres: cliente directo (uso propio)")
            continue
        else:
            print("Bot: No entendi las medidas. Ejemplo: '2x3 metros' o '100x200 cm'")
            continue
    
    # ========== PASO 0: Detectar producto ==========
    if any(p in msg for p in ["adhesivo", "adhesivo laminado", "vinil", "vinilo", "banner", "lona", "pendon", "valla", "aviso", "gran formato"]):
        # Identificar producto
        if "adhesivo" in msg:
            producto_actual = "Adhesivo Laminado"
        elif "vinil" in msg:
            producto_actual = "Vinil"
        elif "banner" in msg:
            producto_actual = "Banner"
        elif "lona" in msg:
            producto_actual = "Lona"
        else:
            producto_actual = "Gran Formato"
        
        # Verificar si tiene medidas en el mismo mensaje
        medidas_encontradas = None
        es_cm = False
        
        patron_cm = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:cm|cms?|centimetros?)'
        match = re.search(patron_cm, msg)
        if match:
            cm1 = float(match.group(1))
            cm2 = float(match.group(2))
            medidas_encontradas = (cm1 / 100.0, cm2 / 100.0)
            es_cm = True
        
        if not medidas_encontradas:
            patron_metros = r'(\d+(?:\.\d+)?)\s*(?:x|por|\*)\s*(\d+(?:\.\d+)?)\s*(?:metros?|m)?'
            match = re.search(patron_metros, msg)
            if match:
                medidas_encontradas = (float(match.group(1)), float(match.group(2)))
                es_cm = False
        
        if medidas_encontradas:
            # Ya tiene medidas
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
            print("Bot: ¿Eres agencia publicitaria o tercero? (SI/NO)")
            continue
        else:
            # No tiene medidas
            paso_cotizacion = 1
            print("")
            print(f"Bot: ✅ Producto: {producto_actual}")
            print("Bot: 📐 Indica las medidas (ejemplo: '2x3 metros' o '100x200 cm'):")
            continue
    
    # ========== PRODUCTOS DEL CATALOGO ==========
    if any(p in msg for p in ["tarjeta", "tarjetas"]):
        prod = PRODUCTOS.get('tarjetas_presentacion', {})
        print(f"""Bot: 💼 {prod.get('nombre', 'Tarjetas de Presentación')}

Precios:
• 100 unidades: ${prod.get('precio_100_unidades', 0):,} COP
• 500 unidades: ${prod.get('precio_500_unidades', 0):,} COP

⏱️ Tiempo: {prod.get('tiempo_entrega', '2-3 días')}

¿Cuantas necesitas?""")
        continue
    
    if any(p in msg for p in ["camiseta", "camisetas", "polo", "polos"]):
        prod = PRODUCTOS.get('camisetas', {})
        print(f"""Bot: 👕 {prod.get('nombre', 'Camisetas Estampadas')}

Precios por unidad:
• Sublimación: ${prod.get('precio_unitario_sublimacion', 0):,} COP
• Serigrafía: ${prod.get('precio_unitario_serigrafia', 0):,} COP

📦 Minimo: {prod.get('minimo_unidades', 12)} unidades
⏱️ Tiempo: {prod.get('tiempo_entrega', '3-5 días')}

¿Para que evento las necesitas?""")
        continue
    
    # ========== CONFIRMACION DE PEDIDO ==========
    if any(p in msg for p in ["si", "sí", "confirmo", "confirmar", "dale", "ok", "esta bien", "me parece", "proceder"]):
        print("")
        print("Bot: 🎉 ¡Perfecto! Pedido confirmado.")
        print("Bot: ")
        print("Bot: 📋 ESTOS SON LOS SIGUIENTES PASOS:")
        print("Bot:    1️⃣  Te enviaremos la cotización formal por WhatsApp/Email")
        print("Bot:    2️⃣  Confirmas el diseño (si aplica)")
        print("Bot:    3️⃣  Realizas el pago del 50% de anticipo")
        print("Bot:    4️⃣  Producimos tu pedido")
        print("Bot:    5️⃣  Te notificamos cuando esté listo para entrega")
        print("Bot: ")
        print(f"Bot: 📱 Nos comunicaremos contigo al: {TELEFONO}")
        print("Bot: ⏱️  Tiempo estimado: 1-3 días hábiles")
        print("Bot: ")
        print("Bot: ¿Tienes el diseño listo o necesitas que lo creemos?")
        continue
    
    # ========== SALUDOS Y MENU ==========
    if any(p in msg for p in ["hola", "buenos dias", "buenas tardes", "buenas noches"]):
        print(f"Bot: ¡Hola! Bienvenido a {NOMBRE_EMPRESA}. ¿En qué puedo ayudarte?")
        continue
    
    # ========== MENU CON NUMEROS ==========
    if any(p in msg for p in ["menu", "opciones", "servicios"]):
        print(f"""Bot: 📋 NUESTROS SERVICIOS - {NOMBRE_EMPRESA}

1️⃣  GRAN FORMATO: Vinil, adhesivos, banners, lonas
    Ejemplo: 'adhesivo 2x3 metros' o 'banner 100x200 cm'

2️⃣  IMPRENTA: Tarjetas, volantes, afiches
3️⃣  TEXTILES: Camisetas, gorras, uniformes
4️⃣  MERCHANDISING: Termos, tazas, agendas
5️⃣  EMPAQUES: Cajas, etiquetas

Escribe el número (1-5) o el nombre del producto para cotizar.""")
        continue
    
    # ========== RESPONDER A NUMEROS DEL MENU ==========
    if msg in ["1", "2", "3", "4", "5"]:
        if msg == "1":
            print("""Bot: 🖨️ GRAN FORMATO

Productos disponibles:
• Vinil adhesivo (blanco o transparente)
• Adhesivo laminado (mate o brillante)
• Banner (PVC flexible)
• Lona front y back
• Microperforado

Para cotizar, escribe:
Ejemplo: 'adhesivo 2x3 metros' o 'vinil 100x200 cm'""")
        elif msg == "2":
            print("""Bot: 📄 IMPRENTA GRAFICA

Productos:
• Tarjetas de presentación
• Volantes / Flyers
• Afiches
• Catálogos

Escribe el producto para ver precios.""")
        elif msg == "3":
            print("""Bot: 👕 TEXTILES

Productos:
• Camisetas estampadas
• Gorras personalizadas
• Uniformes
• Bolsas

Escribe el producto para ver precios.""")
        elif msg == "4":
            print("""Bot: 🎁 MERCHANDISING

Productos:
• Termos personalizados
• Tazas y mugs
• Agendas y libretas
• Bolígrafos corporativos

Escribe el producto para ver precios.""")
        elif msg == "5":
            print("""Bot: 📦 EMPAQUES

Productos:
• Cajas personalizadas
• Etiquetas adhesivas
• Empaque corporativo

Escribe el producto para ver precios.""")
        continue
    
    if any(p in msg for p in ["precio", "costo", "cuanto cuesta"]):
        print(f"""Bot: 💰 NUESTROS PRECIOS:

GRAN FORMATO:
• Cliente directo: ${PRECIO_DIRECTO_M2:,} COP/m²
• Terceros/agencias: ${PRECIO_TERCERO_M2:,} COP/m² (con documentación)

Para otros productos, escribe el nombre: 'tarjetas', 'camisetas', etc.""")
        continue
    
    # ========== CONTACTO ==========
    if any(p in msg for p in ["contacto", "telefono", "whatsapp", "email", "donde estan"]):
        print(f"""Bot: 📞 INFORMACION DE CONTACTO:

📱 WhatsApp: {TELEFONO}
📧 Email: {EMAIL}
📍 Ciudad: {CIUDAD}
🕐 Horario: {HORARIO}""")
        continue
    
    # ========== RESPUESTA POR DEFECTO ==========
    print("Bot: Entiendo. Para ayudarte:")
    print("Bot:    • Escribe 'menu' para ver servicios")
    print("Bot:    • Escribe el producto: 'adhesivo', 'vinil', 'tarjetas'")
    print("Bot:    • O: 'necesito cotizar [producto]'")

print("")
print("=" * 60)
print("  Conversacion finalizada")
print("=" * 60)
