"""
router.py - Logica de enrutamiento y respuestas del bot
Procesa mensajes y genera respuestas segun configuracion del cliente
"""

import re
import random
from datetime import datetime
from typing import Dict, Tuple, Optional
import pytz

# Importar base de datos
try:
    from database import db
except ImportError:
    db = None

# Importar carrito SaaS
try:
    from app.carrito_bot import CarritoBot
except ImportError:
    CarritoBot = None


class MessageRouter:
    """Enruta mensajes y genera respuestas personalizadas."""
    
    def __init__(self, config: Dict, cliente_id: str = None):
        self.config = config
        self.cliente_id = cliente_id
        self.estado = {}  # Estado de la conversacion por usuario
        
        # Inicializar carrito si está disponible
        if CarritoBot:
            self.carrito = CarritoBot(config)
        else:
            self.carrito = None
    
    # ========== FUNCIONES DE CORTESIA ==========
    
    def _obtener_saludo_horario(self) -> str:
        """Genera saludo segun hora del dia (zona horaria Colombia)."""
        # Usar zona horaria de Colombia (America/Bogota)
        tz_colombia = pytz.timezone('America/Bogota')
        hora = datetime.now(tz_colombia).hour
        nombre = self.config.get('nombre', 'Publiya7')
        
        if 6 <= hora < 12:
            return f"¡Buenos días!"
        elif 12 <= hora < 18:
            return f"¡Buenas tardes!"
        else:
            return f"¡Buenas noches!"
    
    def _frase_cortesia(self, tipo: str = "general") -> str:
        """Frases de cortesia personalizables."""
        respuestas_config = self.config.get('respuestas', {})
        
        # Obtener lista de frases para el tipo, o usar defaults
        frases = respuestas_config.get(tipo, [])
        if not frases:
            frases = self._get_frases_default(tipo)
        
        return random.choice(frases)
    
    def _get_frases_default(self, tipo: str) -> list:
        """Frases por defecto si no estan en config."""
        defaults = {
            "general": [
                "Con mucho gusto le ayudo...",
                "Sera un placer atenderle...",
                f"En {self.config.get('nombre')} estamos para servirle..."
            ],
            "cotizando": [
                "Permitame preparar su cotizacion...",
                "Un momento mientras calculo...",
                "Dejeme buscarle la mejor opcion..."
            ],
            "excelente_eleccion": [
                "¡Excelente eleccion! Ese producto tiene muy buena acogida.",
                "¡Muy buen gusto! Es uno de nuestros mas solicitados.",
                "¡Perfecto! Esa es una opcion muy popular."
            ],
            "agradecimiento": [
                f"Gracias por preferir {self.config.get('nombre')}.",
                "Ha sido un gusto atenderle.",
                "Fue un placer ayudarle."
            ],
            "despedida": [
                "Estamos a sus ordenes para cualquier consulta.",
                "Esperamos que se haya sentido bien atendido.",
                "Que tenga un excelente dia."
            ],
            "fallback": [
                "🤔 No entendí bien. Escribe 'menu' para ver las opciones disponibles.",
                "❓ No estoy seguro de qué necesitas. Escribe 'menu' para que te muestre las categorías.",
                "💬 ¿Podrías ser más específico? Escribe 'menu' para ver todos nuestros productos."
            ]
        }
        return defaults.get(tipo, ["¿En que puedo ayudarle?"])
    
    # ========== GENERACION DE MENUS ==========
    
    def generar_menu_principal(self) -> str:
        """Genera menu principal con todas las categorias."""
        saludo = self._obtener_saludo_horario()
        nombre = self.config.get('nombre', 'Publiya7')
        eslogan = self.config.get('eslogan', '')
        
        # Obtener pregunta personalizada o usar default
        mensajes = self.config.get('mensajes', {})
        pregunta = mensajes.get('pregunta', '¿En que podemos ayudarte?')
        
        menu = f"""👋 {saludo} ¡Bienvenido a {nombre}!

{eslogan}

{pregunta}"""
        
        # Emojis para números
        numeros_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        categorias = self.config.get('categorias', {})
        for i, (cat_id, cat_data) in enumerate(categorias.items(), 1):
            emoji_numero = numeros_emojis[i-1] if i <= len(numeros_emojis) else f"{i}."
            menu += f"\n{emoji_numero} {cat_data.get('nombre', cat_id)}"
        
        menu += "\n\nEscribe el número o nombre de la categoría que necesites."
        menu += "\n(También puedes escribir 'menu' en cualquier momento para volver aquí)"
        return menu
    
    def _get_emoji_categoria(self, cat_id: str) -> str:
        """Asigna emoji segun categoria."""
        emojis = {
            'tarjetas': '[TAR]',
            'volantes': '[VOL]',
            'etiquetas': '[ETQ]',
            'cajas': '[CAJ]',
            'gran_formato': '[GRF]',
            'sellos': '[SEL]',
            'banners': '[BAN]',
            'stickers': '[STK]',
            'otros': '[OTR]'
        }
        return emojis.get(cat_id, '-')
    
    def generar_menu_categoria(self, categoria_id: str) -> str:
        """Genera menu de productos para una categoria."""
        categorias = self.config.get('categorias', {})
        cat = categorias.get(categoria_id)
        
        if not cat:
            return self._frase_cortesia('fallback')
        
        menu = f"📋 {cat.get('nombre', 'Productos').upper()}\n\n"
        
        # Emojis para números
        numeros_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        for i, producto in enumerate(cat.get('tipos', []), 1):
            emoji_numero = numeros_emojis[i-1] if i <= len(numeros_emojis) else f"{i}."
            nombre = producto.get('nombre', f'Producto {i}')
            menu += f"{emoji_numero} {nombre}"
            
            # Mostrar precio segun tipo
            tipo_cot = cat.get('tipo_cotizacion', 'cantidad')
            if tipo_cot == 'cantidad':
                if 'precio_1000' in producto:
                    menu += f" - ${producto['precio_1000']:,} por 1000"
                elif 'precio_unitario' in producto:
                    menu += f" - ${producto['precio_unitario']:,} c/u"
            elif tipo_cot == 'medida':
                precio = producto.get('precio_m2', producto.get('precio_cm2', 0))
                unidad = cat.get('unidad', 'unidad')
                menu += f" - ${precio:,}/{unidad}"
            
            menu += "\n"
        
        menu += "\n🎯 Escribe el *número* del producto que deseas."
        menu += "\n\n💡 *Comandos útiles:*\n↩️ Escribe *volver* para regresar\n🏠 Escribe *menu* para ir al inicio"
        return menu
    
    # ========== PROCESAMIENTO DE MENSAJES ==========
    
    def procesar_mensaje(self, mensaje: str, user_id: str = "default", cliente_id: str = None) -> Tuple[str, dict]:
        """
        Procesa un mensaje y retorna respuesta + metadata.
        Carga estado desde BD, procesa, guarda estado y loguea conversacion.
        """
        msg = mensaje.lower().strip()
        cliente_id = cliente_id or self.config.get('cliente_id', 'default')
        
        try:
            # Cargar estado desde BD si existe
            estado = self._cargar_estado(cliente_id, user_id)
            
            # DEBUG: Log estado actual
            print(f"[DEBUG] Usuario: {user_id}, Paso: {estado.get('paso')}, Categoria: {estado.get('categoria')}, Mensaje: {mensaje[:30]}")
            
            # Detectar intencion y procesar
            respuesta, metadata = self._procesar_intencion(msg, estado, cliente_id, user_id)
            
            # DEBUG: Log estado después de procesar
            print(f"[DEBUG] Después - Paso: {estado.get('paso')}, Categoria: {estado.get('categoria')}")
            
            # Guardar estado actualizado
            guardado_ok = self._guardar_estado(cliente_id, user_id, estado)
            
            # Verificar que el estado se guardó correctamente
            if not guardado_ok:
                print(f"[ERROR] CRÍTICO: No se pudo guardar el estado para {cliente_id}/{user_id}")
                # Agregar mensaje de error a la respuesta
                respuesta += "\n\n⚠️ *Nota: Hubo un problema técnico. Si el problema persiste, escribe 'menu' para reiniciar.*"
            
            # Loguear conversacion
            self._loguear_conversacion(cliente_id, user_id, mensaje, respuesta, metadata.get('tipo', 'general'))
            
            return respuesta, metadata
            
        except Exception as e:
            print(f"[ERROR] Error en procesar_mensaje: {e}")
            respuesta = self._frase_cortesia('fallback')
            self._loguear_conversacion(cliente_id, user_id, mensaje, respuesta, 'error')
            return respuesta, {'tipo': 'error', 'error': str(e)}
    
    def _procesar_intencion(self, msg: str, estado: dict, cliente_id: str, user_id: str) -> Tuple[str, dict]:
        """Detecta intencion y procesa el mensaje."""
        
        # Comandos especiales de navegacion
        if msg in ["volver", "atras", "anterior", "regresar"]:
            return self._volver_paso_anterior(estado, cliente_id, user_id)
        
        if msg in ["menu", "inicio", "principal", "empezar"]:
            estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
            return self.generar_menu_principal(), {'tipo': 'saludo'}
        
        # Palabras de cortesia/agradecimiento (solo si no estamos esperando respuesta de nuevo pedido)
        if estado.get('paso') != 4 and any(x in msg for x in ["gracias", "agradezco", "muy amable", "excelente", "perfecto", "genial", "ok", "okay"]):
            return f"{self._frase_cortesia('agradecimiento')} ¿Hay algo mas en lo que pueda ayudarle? Escriba 'menu' para ver las opciones.", {'tipo': 'cortesia'}
        
        # Saludos - reinician la conversacion
        if any(x in msg for x in ["hola", "buenas", "hey", "saludos"]):
            estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
            return self.generar_menu_principal(), {'tipo': 'saludo'}
        
        # Contacto
        if any(x in msg for x in ["contacto", "telefono", "whatsapp", "email"]):
            return self._generar_info_contacto(), {'tipo': 'contacto'}
        
        # Historial de pedidos
        if any(x in msg for x in ["mis pedidos", "historial", "pedidos anteriores", "ver pedidos"]):
            return self._mostrar_historial_pedidos(user_id, cliente_id)
        
        # PASO 0: Seleccionar categoria
        if estado['paso'] == 0:
            return self._procesar_categoria(msg, estado)
        
        # PASO 1: Seleccionar producto
        if estado['paso'] == 1:
            return self._procesar_producto(msg, estado)
        
        # PASO 2: Ingresar cantidad/medida
        if estado['paso'] == 2:
            return self._procesar_cantidad(msg, estado, user_id)
        
        # PASO 3: Confirmar pedido
        if estado['paso'] == 3:
            respuesta, metadata = self._procesar_confirmacion(msg, estado, user_id, cliente_id)
            # Si se confirmo, ir al paso 4 (esperar respuesta de nuevo pedido)
            if metadata.get('tipo') == 'pedido_confirmado':
                estado['paso'] = 4
                self._guardar_estado(cliente_id, user_id, estado)
            # Si se cancelo, limpiar estado
            elif metadata.get('tipo') == 'cancelado':
                self._limpiar_estado(cliente_id, user_id)
                estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
            return respuesta, metadata
        
        # PASO 4: Confirmación final del pedido (después de ver resumen)
        if estado['paso'] == 4:
            # Delegar a _procesar_confirmacion que maneja el carrito
            respuesta, metadata = self._procesar_confirmacion(msg, estado, user_id, cliente_id)
            
            if metadata.get('tipo') == 'pedido_confirmado':
                # Pedido confirmado, limpiar estado y pasar a paso 5 (nuevo pedido)
                estado.update({'paso': 5, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
                self._guardar_estado(cliente_id, user_id, estado)
            elif metadata.get('tipo') == 'ver_carrito':
                # Volver al carrito, mantener paso 3
                estado['paso'] = 3
                self._guardar_estado(cliente_id, user_id, estado)
            
            return respuesta, metadata
        
        # PASO 5: Después de pedido confirmado, preguntar por nuevo pedido
        if estado['paso'] == 5:
            if msg in ["si", "sí", "si"]:
                estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
                self._guardar_estado(cliente_id, user_id, estado)
                return self.generar_menu_principal(), {'tipo': 'nuevo_pedido'}
            elif msg in ["no"]:
                self._limpiar_estado(cliente_id, user_id)
                estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
                return f"{self._frase_cortesia('despedida')} ¡Que tenga un excelente dia!", {'tipo': 'despedida'}
            else:
                return "🛒 ¿Deseas hacer *otro pedido*?\n\n✅ Escribe *si* para ver el menú\n❌ Escribe *no* para finalizar", {'tipo': 'esperando_respuesta'}
        
        # Fallback
        return self._frase_cortesia('fallback'), {'tipo': 'fallback'}
    
    def _volver_paso_anterior(self, estado: dict, cliente_id: str, user_id: str) -> Tuple[str, dict]:
        """Regresa al paso anterior de la conversacion."""
        paso_actual = estado.get('paso', 0)
        
        if paso_actual == 0:
            # Ya estamos en el inicio
            return "🏠 Ya estás en el *menú principal*.\n\n¿En qué puedo ayudarte hoy? 😊", {'tipo': 'info'}
        
        elif paso_actual == 1:
            # Volver al menu principal
            estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
            return self.generar_menu_principal(), {'tipo': 'menu_principal'}
        
        elif paso_actual == 2:
            # Volver a seleccion de productos
            estado['paso'] = 1
            estado['producto'] = None
            estado['cantidad'] = None
            categoria_id = estado.get('categoria')
            if categoria_id:
                return self.generar_menu_categoria(categoria_id), {'tipo': 'menu_categoria'}
            else:
                estado['paso'] = 0
                return self.generar_menu_principal(), {'tipo': 'menu_principal'}
        
        elif paso_actual == 3:
            # Volver a ingresar cantidad
            estado['paso'] = 2
            estado['cantidad'] = None
            estado['total'] = 0
            
            categorias = self.config.get('categorias', {})
            cat = categorias.get(estado.get('categoria'), {})
            tipo_cot = cat.get('tipo_cotizacion', 'cantidad')
            
            if tipo_cot == 'medida':
                prompt = "¿Podria indicarme las medidas? (Ejemplo: 100x200 en cm)"
            elif estado.get('categoria') == 'sellos':
                prompt = "¿Cuantos sellos necesita? (Puede ser 1, 2, 5...)"
            else:
                prompt = "¿Que cantidad necesita? (Ejemplo: 1000, 5000, 10000 unidades)"
            
            return f"[VOLVER] Volvamos a la cantidad.\n\n{prompt}", {'tipo': 'volver'}
        
        return self.generar_menu_principal(), {'tipo': 'menu_principal'}
    
    def _loguear_conversacion(self, cliente_id: str, user_id: str, mensaje: str, respuesta: str, tipo: str):
        """Guarda la conversacion en BD para auditoria."""
        try:
            if db:
                db.guardar_conversacion(cliente_id, user_id, mensaje, respuesta, tipo)
        except Exception as e:
            print(f"[ERROR] No se pudo loguear conversacion: {e}")
    
    def _cargar_estado(self, cliente_id: str, user_id: str) -> Dict:
        """Carga estado desde BD o crea uno nuevo."""
        if db:
            try:
                estado_bd = db.obtener_estado(cliente_id, user_id)
                if estado_bd:
                    print(f"[DEBUG] Estado cargado: {cliente_id}/{user_id} - paso {estado_bd.get('paso')} - cat {estado_bd.get('categoria')}")
                    return {
                        'paso': estado_bd.get('paso', 0),
                        'categoria': estado_bd.get('categoria'),
                        'producto': estado_bd.get('producto'),
                        'cantidad': estado_bd.get('cantidad'),
                        'total': estado_bd.get('total', 0),
                        'datos_extra': estado_bd.get('datos_extra', {})
                    }
                else:
                    print(f"[DEBUG] No hay estado previo para {cliente_id}/{user_id}, creando nuevo")
            except Exception as e:
                print(f"[ERROR] Excepción cargando estado: {e}")
        else:
            print(f"[WARNING] db es None, no se puede cargar estado")
        
        # Estado por defecto
        return {'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0}
    
    def _guardar_estado(self, cliente_id: str, user_id: str, estado: Dict) -> bool:
        """Guarda estado en BD. Retorna True si se guardó correctamente."""
        if db:
            try:
                resultado = db.guardar_estado(cliente_id, user_id, estado)
                if not resultado:
                    print(f"[ERROR] No se pudo guardar el estado para {cliente_id}/{user_id}")
                    return False
                else:
                    print(f"[DEBUG] Estado guardado OK: {cliente_id}/{user_id} - paso {estado.get('paso')} - cat {estado.get('categoria')}")
                    return True
            except Exception as e:
                print(f"[ERROR] Excepción guardando estado: {e}")
                return False
        else:
            print(f"[ERROR] db es None, no se puede guardar estado")
            return False
    
    def _limpiar_estado(self, cliente_id: str, user_id: str):
        """Limpia estado de la BD."""
        if db:
            db.limpiar_estado(cliente_id, user_id)
    
    def _procesar_categoria(self, msg: str, estado: dict) -> Tuple[str, dict]:
        """Procesa seleccion de categoria."""
        categorias = self.config.get('categorias', {})
        
        # Buscar por numero
        try:
            num = int(msg)
            cat_list = list(categorias.items())
            if 1 <= num <= len(cat_list):
                cat_id = cat_list[num - 1][0]
                estado['categoria'] = cat_id
                estado['paso'] = 1
                return self.generar_menu_categoria(cat_id), {'tipo': 'menu_categoria', 'categoria': cat_id}
        except ValueError:
            pass
        
        # Buscar por nombre
        for cat_id, cat_data in categorias.items():
            if cat_id in msg or cat_data.get('nombre', '').lower() in msg:
                estado['categoria'] = cat_id
                estado['paso'] = 1
                return self.generar_menu_categoria(cat_id), {'tipo': 'menu_categoria', 'categoria': cat_id}
        
        return f"Disculpe, no reconoci esa categoria. {self._frase_cortesia('general')}", {'tipo': 'error'}
    
    def _procesar_producto(self, msg: str, estado: dict) -> Tuple[str, dict]:
        """Procesa seleccion de producto."""
        try:
            opcion = int(re.search(r'(\d+)', msg).group(1)) - 1
            cat_id = estado['categoria']
            categorias = self.config.get('categorias', {})
            cat = categorias.get(cat_id, {})
            tipos = cat.get('tipos', [])
            
            if 0 <= opcion < len(tipos):
                estado['producto'] = opcion
                estado['paso'] = 2
                producto = tipos[opcion]
                
                # Verificar si requiere cotizacion personalizada
                if producto.get('requiere_cotizacion'):
                    return f"[COTIZACION PERSONALIZADA]\n\n{producto['nombre']}\n\nEste producto requiere cotizacion personalizada. Por favor contactenos al {self.config.get('telefono')}.", {'tipo': 'cotizacion_personalizada'}
                
                tipo_cot = cat.get('tipo_cotizacion', 'cantidad')
                if tipo_cot == 'medida':
                    prompt = "¿Podria indicarme las medidas? (Ejemplo: 100x200 en cm)"
                elif cat_id == 'sellos':
                    prompt = "¿Cuantos sellos necesita? (Puede ser 1, 2, 5...)"
                else:
                    prompt = "¿Que cantidad necesita? (Ejemplo: 1000, 5000, 10000 unidades)"
                
                return f"[OK] {producto.get('nombre')}\n\n{self._frase_cortesia('excelente_eleccion')}\n\n{prompt}", {'tipo': 'producto_seleccionado'}
        except:
            pass
        
        return "🎯 Por favor escribe el *número* del producto que deseas.\n\n💡 También puedes escribir:\n↩️ *volver* - para regresar\n🏠 *menu* - para ir al inicio", {'tipo': 'error'}
    
    def _procesar_cantidad(self, msg: str, estado: dict, user_id: str = None) -> Tuple[str, dict]:
        """Procesa cantidad o medidas y agrega al carrito."""
        cat_id = estado['categoria']
        categorias = self.config.get('categorias', {})
        cat = categorias.get(cat_id, {})
        tipo_cot = cat.get('tipo_cotizacion', 'cantidad')
        
        if tipo_cot == 'medida':
            # Procesar medidas (ej: 100x200)
            medidas = re.search(r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)', msg)
            if medidas:
                ancho = float(medidas.group(1))
                alto = float(medidas.group(2))
                estado['cantidad'] = f"{ancho}x{alto}cm"
                estado['total'] = self._calcular_precio(estado, ancho * alto)
                estado['paso'] = 3
                
                # Agregar al carrito si está disponible
                print(f"[DEBUG] Carrito check: carrito={self.carrito is not None}, user_id={user_id}, cliente_id={self.cliente_id}")
                if self.carrito and user_id and self.cliente_id:
                    print(f"[DEBUG] Agregando al carrito...")
                    return self._agregar_al_carrito(estado, user_id, area=ancho*alto)
                else:
                    print(f"[DEBUG] Carrito no disponible, usando cotizacion normal")
                
                return self._generar_cotizacion(estado, area=ancho*alto), {'tipo': 'cotizacion'}
            else:
                return f"Disculpe, necesito las medidas. {self._frase_cortesia('general')}\n\nEjemplo: 100x200 o 150x300 (en cm)", {'tipo': 'error'}
        else:
            # Procesar cantidad numerica
            num = re.search(r'(\d+)', msg)
            if num:
                estado['cantidad'] = int(num.group(1))
                estado['total'] = self._calcular_precio(estado)
                estado['paso'] = 3
                
                # Agregar al carrito si está disponible
                print(f"[DEBUG] Carrito check: carrito={self.carrito is not None}, user_id={user_id}, cliente_id={self.cliente_id}")
                if self.carrito and user_id and self.cliente_id:
                    print(f"[DEBUG] Agregando al carrito...")
                    return self._agregar_al_carrito(estado, user_id)
                else:
                    print(f"[DEBUG] Carrito no disponible, usando cotizacion normal")
                
                return self._generar_cotizacion(estado), {'tipo': 'cotizacion'}
            else:
                return f"Disculpe, necesito la cantidad. {self._frase_cortesia('general')}\n\nEjemplo: 1000, 5000, 10000", {'tipo': 'error'}
    
    def _agregar_al_carrito(self, estado: dict, user_id: str, area: int = None) -> Tuple[str, dict]:
        """Agrega producto al carrito y retorna mensaje con opciones."""
        try:
            mensaje = self.carrito.agregar_producto(
                cliente_id=self.cliente_id,
                user_id=user_id,
                estado=estado,
                area=area
            )
            return mensaje, {'tipo': 'carrito'}
        except Exception as e:
            print(f"[ERROR] Error agregando al carrito: {e}")
            # Fallback a cotización normal
            if area:
                return self._generar_cotizacion(estado, area=area), {'tipo': 'cotizacion'}
            else:
                return self._generar_cotizacion(estado), {'tipo': 'cotizacion'}
    
    def _procesar_confirmacion(self, msg: str, estado: dict, user_id: str, cliente_id: str) -> Tuple[str, dict]:
        """Procesa opciones del carrito: 1-Otro, 2-Ver, 3-Finalizar, 4-Cancelar."""
        
        # PRIMERO: Verificar si estamos en confirmación final (paso 4)
        if estado.get('paso') == 4:
            if msg in ["si", "sí", "si", "1", "1️⃣"]:
                # Confirmar pedido
                return self._finalizar_pedido_carrito(user_id, cliente_id)
            elif msg in ["no", "2", "2️⃣"]:
                # Volver al carrito
                estado['paso'] = 3
                if self.carrito:
                    mensaje = self.carrito.ver_carrito(cliente_id, user_id)
                    return mensaje, {'tipo': 'ver_carrito'}
                return "🛒 *¿Qué deseas hacer?*\n\n1️⃣ Agregar *OTRO* producto\n2️⃣ *VER* carrito\n3️⃣ *FINALIZAR* pedido\n4️⃣ *CANCELAR* todo", {'tipo': 'carrito'}
            elif msg in ["cancelar", "3", "3️⃣"]:
                # Cancelar todo
                if self.carrito:
                    mensaje = self.carrito.cancelar_carrito(cliente_id, user_id)
                else:
                    mensaje = "Carrito cancelado."
                estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
                return mensaje, {'tipo': 'carrito_cancelado'}
        
        # Opciones del carrito (después de agregar producto, paso 3)
        # Mensaje muestra: 1-Otro, 2-Ver, 3-Finalizar, 4-Cancelar
        if msg in ["1", "1️⃣", "otro", "agregar", "mas", "agregar otro"]:
            # Volver a seleccionar categoría
            estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
            return self.generar_menu_principal(), {'tipo': 'menu_principal'}
        
        elif msg in ["2", "2️⃣", "ver", "carrito", "ver carrito"]:
            # Ver carrito
            if self.carrito:
                mensaje = self.carrito.ver_carrito(cliente_id, user_id)
                return mensaje, {'tipo': 'ver_carrito'}
            else:
                return "🛒 Carrito no disponible.", {'tipo': 'error'}
        
        elif msg in ["3", "3️⃣", "finalizar", "pedido", "comprar", "finalizar pedido"]:
            # Finalizar pedido - mostrar resumen
            if self.carrito:
                mensaje = self.carrito.ver_carrito(cliente_id, user_id, mostrar_resumen=True)
                estado['paso'] = 4  # Ir a confirmación final
                return mensaje, {'tipo': 'resumen_pedido'}
            else:
                # Fallback a pedido simple
                return self._finalizar_pedido_simple(estado, user_id, cliente_id)
        
        elif msg in ["4", "4️⃣", "cancelar", "eliminar", "cancelar carrito"]:
            # Cancelar carrito
            if self.carrito:
                mensaje = self.carrito.cancelar_carrito(cliente_id, user_id)
            else:
                mensaje = "Carrito cancelado. Escribe 'menu' para empezar de nuevo."
            estado.update({'paso': 0, 'categoria': None, 'producto': None, 'cantidad': None, 'total': 0})
            return mensaje, {'tipo': 'carrito_cancelado'}
        
        else:
            return "🛒 ¿Qué deseas hacer?\n1️⃣ Agregar OTRO producto\n2️⃣ VER carrito\n3️⃣ FINALIZAR pedido\n4️⃣ CANCELAR", {'tipo': 'carrito'}
    
    def _finalizar_pedido_carrito(self, user_id: str, cliente_id: str) -> Tuple[str, dict]:
        """Finaliza el pedido desde el carrito."""
        if self.carrito:
            try:
                mensaje = self.carrito.finalizar_pedido(cliente_id, user_id)
                return mensaje, {'tipo': 'pedido_confirmado'}
            except Exception as e:
                print(f"[ERROR] Error finalizando pedido: {e}")
                return "❌ *Error al procesar el pedido.*\n\nPor favor intenta de nuevo o escribe *menu* para reiniciar. 🔄", {'tipo': 'error'}
        else:
            return self._finalizar_pedido_simple({}, user_id, cliente_id)
    
    def _finalizar_pedido_simple(self, estado: dict, user_id: str, cliente_id: str) -> Tuple[str, dict]:
        """Finaliza pedido simple (sin carrito) - fallback."""
        numero_orden = None
        
        # Guardar pedido en BD
        if db:
            try:
                numero_orden = db.guardar_pedido(
                    cliente_id=cliente_id,
                    user_id=user_id,
                    producto=estado.get('categoria', ''),
                    tipo=str(estado.get('producto', '')),
                    cantidad=str(estado.get('cantidad', '')),
                    precio_total=estado.get('total', 0),
                    notas="Pedido generado por bot"
                )
            except Exception as e:
                print(f"[ERROR] Error guardando pedido: {e}")
        
        # Fallback si no hay BD
        if not numero_orden:
            from datetime import datetime
            import random
            numero_orden = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
        
        respuesta = f"""🎉 ¡PEDIDO CONFIRMADO!

📦 Número de Orden: {numero_orden}
💰 Total: ${estado.get('total', 0):,} COP

{self._frase_cortesia('agradecimiento')}

¿Deseas realizar otro pedido? Escribe 'si' para ver el menú o 'no' para finalizar."""
        
        return respuesta, {'tipo': 'pedido_confirmado', 'orden': numero_orden}
    
    def _calcular_precio(self, estado: dict, area: int = None) -> int:
        """Calcula el precio segun configuracion."""
        cat_id = estado['categoria']
        prod_idx = estado['producto']
        cantidad = estado['cantidad']
        
        categorias = self.config.get('categorias', {})
        cat = categorias.get(cat_id, {})
        tipos = cat.get('tipos', [])
        
        if prod_idx >= len(tipos):
            return 0
        
        producto = tipos[prod_idx]
        tipo_cot = cat.get('tipo_cotizacion', 'cantidad')
        
        if tipo_cot == 'medida' and area:
            # Por metro cuadrado o cm cuadrado
            precio_unidad = producto.get('precio_m2', producto.get('precio_cm2', 0))
            return int(area * precio_unidad)
        elif tipo_cot == 'medida':
            # Tipo medida pero sin area - no se puede calcular
            return 0
        else:
            # Por cantidad
            base = cat.get('unidad_base', 1000)
            
            # Si tiene precio unitario (etiquetas, cajas, sellos)
            if 'precio_unitario' in producto:
                return int(producto['precio_unitario'] * cantidad)
            
            # Calcular precio por unidad segun rangos de cantidad
            if isinstance(cantidad, int):
                # Obtener precio por unidad segun el rango
                if cantidad >= 5000:
                    # Usar precio con descuento de 5000 si existe, sino calcular proporcional
                    if 'precio_5000' in producto:
                        precio_por_unidad = producto['precio_5000'] / 5000
                    else:
                        precio_por_unidad = producto.get('precio_1000', 0) / 1000
                elif cantidad >= 2000:
                    # Usar precio con descuento de 2000 si existe
                    if 'precio_2000' in producto:
                        precio_por_unidad = producto['precio_2000'] / 2000
                    else:
                        precio_por_unidad = producto.get('precio_1000', 0) / 1000
                else:
                    # Precio base por 1000 unidades
                    precio_por_unidad = producto.get('precio_1000', 0) / 1000
                
                return int(precio_por_unidad * cantidad)
        
        return 0
    
    def _calcular_tiempo_entrega(self, categoria_id: str, cantidad: int) -> str:
        """Calcula el tiempo de entrega segun categoria y cantidad."""
        
        # Tiempos especificos para Cajas
        if categoria_id == "cajas":
            if cantidad <= 2000:
                return "5-10 dias habiles"
            elif cantidad <= 5000:
                return "7-15 dias habiles"
            elif cantidad <= 8000:
                return "10-20 dias habiles"
            else:
                return "15-25 dias habiles (confirmaremos al revisar su pedido)"
        
        # Default para otras categorias
        return self.config.get('tiempo_entrega_default', '2-5 dias habiles')
    
    def _generar_cotizacion(self, estado: dict, area: int = None) -> str:
        """Genera texto de cotizacion con tiempo de entrega ajustado y descuento."""
        cat_id = estado['categoria']
        prod_idx = estado['producto']
        cantidad = estado['cantidad']
        total = estado['total']
        
        categorias = self.config.get('categorias', {})
        cat = categorias.get(cat_id, {})
        producto = cat.get('tipos', [])[prod_idx]
        
        if area:
            cantidad_str = f"{cantidad} (Area: {area:,} cm2)"
        else:
            cantidad_str = f"{cantidad:,} unidades"
        
        # Calcular tiempo de entrega segun categoria y cantidad
        tiempo_entrega = self._calcular_tiempo_entrega(cat_id, cantidad if isinstance(cantidad, int) else 0)
        
        # Calcular descuento aplicado (solo para cantidades numericas, no para medidas)
        if isinstance(cantidad, int):
            descuento_info = self._calcular_descuento_info(producto, cantidad, cat.get('unidad_base', 1000))
        else:
            descuento_info = None
        
        if descuento_info:
            return f"""[COTIZACION]

{self._frase_cortesia('cotizando')}

• Producto: {producto.get('nombre')}
• Cantidad: {cantidad_str}
• Precio base: ${descuento_info['precio_base']:,} COP
• Descuento aplicado: {descuento_info['porcentaje_descuento']}%
• Total: ${total:,} COP

Tiempo de entrega: {tiempo_entrega}

¿Confirma el pedido? Escriba 'si' o 'no'."""
        else:
            return f"""[COTIZACION]

{self._frase_cortesia('cotizando')}

• Producto: {producto.get('nombre')}
• Cantidad: {cantidad_str}
• Total: ${total:,} COP

Tiempo de entrega: {tiempo_entrega}

¿Confirma el pedido? Escriba 'si' o 'no'."""
    
    def _calcular_descuento_info(self, producto: dict, cantidad: int, base: int) -> dict:
        """Calcula informacion del descuento aplicado."""
        precio_1000 = producto.get('precio_1000', 0)
        
        if cantidad >= 5000 and 'precio_5000' in producto:
            # 10% de descuento para 5000+
            precio_con_descuento = producto['precio_5000']
            precio_sin_descuento = precio_1000 * (cantidad / 1000)
            return {
                'precio_base': int(precio_sin_descuento),
                'porcentaje_descuento': 10
            }
        elif cantidad >= 2000 and 'precio_2000' in producto:
            # 5% de descuento para 2000+
            precio_con_descuento = producto['precio_2000']
            precio_sin_descuento = precio_1000 * (cantidad / 1000)
            return {
                'precio_base': int(precio_sin_descuento),
                'porcentaje_descuento': 5
            }
        
        return None
    
    def _generar_info_contacto(self) -> str:
        """Genera informacion de contacto."""
        return f"""{self._frase_cortesia('general')}

Telefono: {self.config.get('telefono')}
Email: {self.config.get('email')}
Ubicacion: {self.config.get('ciudad')}, {self.config.get('departamento')}
Horario: {self.config.get('horario_atencion', {}).get('lunes_viernes', 'Consultar')}

{self._frase_cortesia('agradecimiento')}"""
    
    def _mostrar_historial_pedidos(self, user_id: str, cliente_id: str) -> Tuple[str, dict]:
        """Muestra el historial de pedidos del usuario."""
        try:
            from database.database_saas import db_saas
            conn = db_saas._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT numero_orden, total, estado, creado_en 
                FROM pedidos 
                WHERE cliente_id = ? AND usuario_id = ?
                ORDER BY creado_en DESC LIMIT 5
            """, (cliente_id, user_id))
            
            pedidos = cursor.fetchall()
            conn.close()
            
            if not pedidos:
                return "📭 No tienes pedidos registrados.\n\nEscribe 'menu' para hacer tu primer pedido.", {'tipo': 'historial_vacio'}
            
            mensaje = "📋 *TUS ÚLTIMOS PEDIDOS*\n\n"
            for p in pedidos:
                estado_icono = {
                    'confirmado': '✅',
                    'pendiente': '⏳',
                    'procesando': '⚙️',
                    'completado': '📦',
                    'cancelado': '❌'
                }.get(p['estado'], '❓')
                
                mensaje += f"{estado_icono} *{p['numero_orden']}*\n"
                mensaje += f"   💰 ${p['total']:,} COP\n"
                mensaje += f"   📅 {p['creado_en'][:10]}\n"
                mensaje += f"   🏷️ {p['estado'].upper()}\n\n"
            
            mensaje += "¿Quieres hacer un nuevo pedido? Escribe 'menu'."
            return mensaje, {'tipo': 'historial'}
            
        except Exception as e:
            print(f"[ERROR] Mostrando historial: {e}")
            return "❌ Error al cargar tu historial. Intenta de nuevo.", {'tipo': 'error'}


# Prueba
if __name__ == "__main__":
    from loader import get_config
    
    print("="*70)
    print("PRUEBA DE ROUTER")
    print("="*70)
    
    config = get_config('publiya7')
    if config:
        router = MessageRouter(config)
        
        print("\nUsuario: hola")
        resp, meta = router.procesar_mensaje("hola", "user1")
        print(f"Bot: {resp[:200]}...")
        print(f"[Tipo: {meta['tipo']}]")
