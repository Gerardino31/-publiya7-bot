"""
loader.py - Carga y normalización de configuración de clientes
Adapta cualquier formato de JSON al formato estándar del bot
"""

import json
import os
from typing import Dict, Optional


class ConfigLoader:
    """Carga y normaliza configuración de clientes."""
    
    def __init__(self, config_dir: str = "clientes/configs"):
        self.config_dir = config_dir
    
    def cargar_config(self, cliente_id: str) -> Optional[Dict]:
        """
        Carga y normaliza la configuración de un cliente.
        
        Args:
            cliente_id: Identificador del cliente (ej: 'publiya7')
        
        Returns:
            Diccionario normalizado con la configuración
        """
        config_path = os.path.join(self.config_dir, f"{cliente_id}.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_raw = json.load(f)
            
            # Normalizar al formato estándar
            config = self._normalizar_config(config_raw, cliente_id)
            return config
            
        except FileNotFoundError:
            print(f"[ERROR] No se encontro configuracion para '{cliente_id}'")
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON mal formado: {e}")
            return None
    
    def _normalizar_config(self, config: Dict, cliente_id: str) -> Dict:
        """
        Normaliza cualquier formato de configuración al estándar.
        Esto permite que cada cliente tenga su propio formato.
        """
        normalizado = {
            'cliente_id': cliente_id,
            'nombre': config.get('nombre') or config.get('nombre_empresa', 'Empresa'),
            'eslogan': config.get('eslogan') or config.get('slogan', ''),
            'ciudad': config.get('ciudad', ''),
            'departamento': config.get('departamento', ''),
            'pais': config.get('pais', 'Colombia'),
            'telefono': config.get('telefono') or config.get('whatsapp', ''),
            'telefono_secundario': config.get('telefono_secundario', ''),
            'whatsapp': config.get('whatsapp', ''),
            'email': config.get('email', ''),
            'direccion': config.get('direccion', ''),
            'horario_atencion': config.get('horario_atencion', {}),
            'instagram': config.get('instagram', ''),
            'facebook': config.get('facebook', ''),
            'tiktok': config.get('tiktok', ''),
            'sitio_web': config.get('sitio_web', ''),
            'nota_precios': config.get('nota_precios', ''),
            'tiempo_entrega_default': config.get('tiempo_entrega_default', '2-5 dias habiles'),
            'moneda': config.get('moneda', 'COP'),
            'metodos_pago': config.get('metodos_pago', ['Efectivo', 'Transferencia']),
        }
        
        # Normalizar categorías de productos
        normalizado['categorias'] = self._normalizar_categorias(config)
        
        # Normalizar respuestas/cortesía
        normalizado['respuestas'] = self._normalizar_respuestas(config)
        
        # Normalizar políticas
        normalizado['politicas'] = config.get('politicas', {
            'anticipo_minimo': 0.50,
            'revisiones_diseno': 2
        })
        
        return normalizado
    
    def _normalizar_categorias(self, config: Dict) -> Dict:
        """
        Normaliza las categorías de productos.
        Soporta múltiples formatos de entrada.
        """
        categorias = {}
        
        # Formato 1: categorias ya definidas
        if 'categorias' in config and isinstance(config['categorias'], dict):
            return config['categorias']
        
        # Formato 2: precios anidados (formato original de Publiya7)
        if 'precios' in config:
            precios = config['precios']
            
            # Tarjetas
            if 'tarjetas_presentacion_1000_unid' in precios:
                categorias['tarjetas'] = {
                    'nombre': 'Tarjetas de Presentacion',
                    'tipo_cotizacion': 'cantidad',
                    'unidad_base': 1000,
                    'tipos': self._extraer_tarjetas(precios['tarjetas_presentacion_1000_unid'])
                }
            
            # Volantes
            if 'volantes_propalcote_115gr_1000_unid' in precios:
                categorias['volantes'] = {
                    'nombre': 'Volantes y Plegables',
                    'tipo_cotizacion': 'cantidad',
                    'unidad_base': 1000,
                    'tipos': self._extraer_volantes(precios['volantes_propalcote_115gr_1000_unid'])
                }
            
            # Gran formato
            if 'gran_formato' in precios:
                categorias['gran_formato'] = {
                    'nombre': 'Gran Formato',
                    'tipo_cotizacion': 'medida',
                    'unidad': 'cm2',
                    'tipos': self._extraer_gran_formato(precios['gran_formato'])
                }
            
            # Sellos
            if 'sellos_automaticos' in precios:
                categorias['sellos'] = {
                    'nombre': 'Sellos Automaticos',
                    'tipo_cotizacion': 'cantidad',
                    'unidad_base': 1,
                    'tipos': self._extraer_sellos(precios['sellos_automaticos'])
                }
            
            # Etiquetas
            if 'etiquetas' in precios:
                categorias['etiquetas'] = {
                    'nombre': 'Etiquetas',
                    'tipo_cotizacion': 'cantidad',
                    'unidad_base': 1,
                    'tipos': self._extraer_etiquetas(precios['etiquetas'])
                }
            
            # Cajas
            if 'cajas' in precios:
                categorias['cajas'] = {
                    'nombre': 'Cajas',
                    'tipo_cotizacion': 'cantidad',
                    'unidad_base': 1,
                    'tipos': self._extraer_cajas(precios['cajas'])
                }
        
        # Formato 3: productos simples
        if 'productos' in config:
            categorias['otros'] = {
                'nombre': 'Otros Productos',
                'tipo_cotizacion': 'personalizado',
                'tipos': [
                    {'id': k, 'nombre': v, 'requiere_cotizacion': True}
                    for k, v in config['productos'].items()
                ]
            }
        
        return categorias
    
    def _extraer_tarjetas(self, data: Dict) -> list:
        """Extrae tipos de tarjetas del formato original."""
        tipos = []
        
        # Sencillas
        if 'propalcote_300gr_9x5cm' in data:
            base = data['propalcote_300gr_9x5cm']
            tipos.extend([
                {'id': 'sencilla_uv_1', 'nombre': 'Sencilla Brillo UV - 1 cara', 'precio_1000': base.get('sencilla_brillo_uv_1_cara', 75000)},
                {'id': 'sencilla_uv_2', 'nombre': 'Sencilla Brillo UV - 2 caras', 'precio_1000': base.get('sencilla_brillo_uv_2_caras', 85000)},
                {'id': 'mate_1', 'nombre': 'Mate - 1 cara', 'precio_1000': base.get('mate_1_cara', 119000)},
                {'id': 'mate_2', 'nombre': 'Mate - 2 caras', 'precio_1000': base.get('mate_2_caras', 130000)},
                {'id': 'mate_reserva_1', 'nombre': 'Mate con Reserva UV - 1 cara', 'precio_1000': base.get('mate_con_reserva_1_cara', 145000)},
                {'id': 'mate_reserva_2', 'nombre': 'Mate con Reserva UV - 2 caras', 'precio_1000': base.get('mate_con_reserva_2_caras', 165000)},
            ])
        
        # Estampadas
        if 'estampada_1_lado' in data:
            tipos.append({'id': 'estampada_1', 'nombre': 'Estampada Dorado/Plateado - 1 lado', 'precio_1000': data['estampada_1_lado']})
        if 'estampada_2_lados' in data:
            tipos.append({'id': 'estampada_2', 'nombre': 'Estampada Dorado/Plateado - 2 lados', 'precio_1000': data['estampada_2_lados']})
        if 'lamindada' in data:
            tipos.append({'id': 'imanadas', 'nombre': 'Imanadas', 'precio_1000': data['lamindada']})
        
        return tipos
    
    def _extraer_volantes(self, data: Dict) -> list:
        """Extrae tipos de volantes."""
        mapeo = {
            '1_cara_4x0_13x7': '1 cara 13x7cm',
            '2_caras_4x4_13x7': '2 caras 13x7cm',
            '1_cara_4x0_21x10': '1 cara 21x10cm',
            '2_caras_4x4_21x10': '2 caras 21x10cm',
            '2_caras_4x4_21x12': '2 caras 21x12cm',
            '1_cara_4x0_21x12': '1 cara 21x12cm',
            '1_cara_4x0_21x13': '1 cara 21x13cm',
            '2_caras_4x4_21x13': '2 caras 21x13cm',
        }
        
        tipos = []
        for key, nombre in mapeo.items():
            if key in data:
                tipos.append({'id': key, 'nombre': nombre, 'precio_1000': data[key]})
        
        return tipos
    
    def _extraer_gran_formato(self, data: Dict) -> list:
        """Extrae tipos de gran formato."""
        tipos = []
        
        if 'banner' in data:
            banner = data['banner']
            tipos.extend([
                {'id': 'banner_term', 'nombre': 'Banner con terminado', 'precio_cm2': banner.get('cm2_con_terminado', 8.5)},
                {'id': 'banner_sin', 'nombre': 'Banner sin terminado', 'precio_cm2': banner.get('cm2_sin_terminado', 7.5)},
            ])
        
        if 'panaflex' in data:
            tipos.append({'id': 'panaflex', 'nombre': 'Panaflex', 'precio_cm2': data['panaflex'].get('cm2', 10)})
        
        if 'adhesivo' in data:
            adhesivo = data['adhesivo']
            tipos.extend([
                {'id': 'adhesivo_sin', 'nombre': 'Adhesivo sin laminar', 'precio_cm2': adhesivo.get('sin_laminar_cm2', 7.5)},
                {'id': 'adhesivo_lam', 'nombre': 'Adhesivo laminado', 'precio_cm2': adhesivo.get('laminado_cm2', 9.4)},
                {'id': 'adhesivo_cont', 'nombre': 'Adhesivo laminado con contorno', 'precio_cm2': adhesivo.get('laminado_con_contorno_cm2', 12)},
            ])
        
        if 'microperforado' in data:
            tipos.append({'id': 'microperf', 'nombre': 'Microperforado', 'precio_cm2': data['microperforado'].get('cm2', 10)})
        
        return tipos
    
    def _extraer_sellos(self, data: Dict) -> list:
        """Extrae tipos de sellos."""
        return [
            {'id': f'sello_{k.replace("x", "_")}', 'nombre': k, 'precio_unitario': v}
            for k, v in data.items()
        ]
    
    def _extraer_etiquetas(self, data: Dict) -> list:
        """Extrae rangos de etiquetas."""
        return [
            {'id': 'et_1000_3000', 'nombre': '1.000 a 3.000 unidades', 'precio_unitario': data.get('1000_a_3000_unid', 550)},
            {'id': 'et_4000_6000', 'nombre': '4.000 a 6.000 unidades', 'precio_unitario': data.get('4000_a_6000_unid', 480)},
            {'id': 'et_7000_9000', 'nombre': '7.000 a 9.000 unidades', 'precio_unitario': data.get('7000_a_9000_unid', 450)},
            {'id': 'et_10000', 'nombre': 'Desde 10.000 unidades', 'precio_unitario': data.get('desde_10000_unid', 350)},
        ]
    
    def _extraer_cajas(self, data: Dict) -> list:
        """Extrae rangos de cajas."""
        return [
            {'id': 'caj_1000_2000', 'nombre': '1.000 a 2.000 unidades', 'precio_unitario': data.get('1000_a_2000_unid', 1000)},
            {'id': 'caj_3000_5000', 'nombre': '3.000 a 5.000 unidades', 'precio_unitario': data.get('3000_a_5000_unid', 950)},
            {'id': 'caj_6000_8000', 'nombre': '6.000 a 8.000 unidades', 'precio_unitario': data.get('6000_a_8000_unid', 900)},
            {'id': 'caj_9000', 'nombre': 'Mas de 9.000 unidades', 'precio_unitario': data.get('desde_9000_unid', 850)},
        ]
    
    def _normalizar_respuestas(self, config: Dict) -> Dict:
        """Normaliza las respuestas de cortesía."""
        if 'respuestas' in config:
            return config['respuestas']
        
        if 'mensajes' in config:
            mensajes = config['mensajes']
            return {
                'fallback': [mensajes.get('fallback', 'No entendi, puede repetir?')],
                'cortesia_general': [mensajes.get('bienvenida', 'Bienvenido')],
                'agradecimiento': [mensajes.get('despedida', 'Gracias')],
            }
        
        # Defaults
        return {
            'fallback': ['Disculpe, no entendi bien. Puede repetir?'],
            'cortesia_general': ['Con gusto le ayudo...'],
            'cotizando': ['Permitame preparar su cotizacion...'],
            'excelente_eleccion': ['Excelente eleccion!'],
            'agradecimiento': ['Gracias por preferirnos.'],
            'despedida': ['Estamos a sus ordenes.'],
        }
    
    def listar_clientes(self) -> list:
        """Lista todos los clientes disponibles."""
        clientes = []
        try:
            for archivo in os.listdir(self.config_dir):
                if archivo.endswith('.json'):
                    cliente_id = archivo.replace('.json', '')
                    clientes.append(cliente_id)
        except FileNotFoundError:
            print(f"[ERROR] No existe el directorio {self.config_dir}")
        return clientes


# Instancia global
loader = ConfigLoader()


def get_config(cliente_id: str = None) -> Dict:
    """
    Funcion helper para obtener configuracion normalizada.
    Si no se especifica cliente_id, usa la variable de entorno CLIENTE_ID.
    """
    if cliente_id is None:
        cliente_id = os.getenv('CLIENTE_ID', 'publiya7')
    
    return loader.cargar_config(cliente_id)


# Prueba
if __name__ == "__main__":
    print("="*70)
    print("PRUEBA DE LOADER CON NORMALIZACION")
    print("="*70)
    
    # Probar con Publiya7 (formato original)
    print("\n1. Cargando Publiya7 (formato original)...")
    config = get_config('publiya7')
    
    if config:
        print(f"[OK] Configuracion normalizada:")
        print(f"   Nombre: {config['nombre']}")
        print(f"   Ciudad: {config['ciudad']}")
        print(f"   Categorias: {list(config['categorias'].keys())}")
        
        # Mostrar primer producto de cada categoria
        print("\n   Productos disponibles:")
        for cat_id, cat in config['categorias'].items():
            tipos = cat.get('tipos', [])
            if tipos:
                print(f"   - {cat['nombre']}: {len(tipos)} tipos")
    else:
        print("[ERROR] No se pudo cargar")
