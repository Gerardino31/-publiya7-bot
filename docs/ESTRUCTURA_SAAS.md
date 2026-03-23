# Estructura SaaS - Bot Multi-Cliente para Imprentas

## 📁 Organización de Archivos

```
automatizacion-mensajeria/
│
├── 📁 clientes/
│   └── 📁 configs/
│       ├── 📄 publiya7.json          ← Cliente 1 (Medellín)
│       ├── 📄 imprentaxyz.json       ← Cliente 2 (Bogotá)
│       ├── 📄 graficasur.json        ← Cliente 3 (Cali)
│       └── 📄 ...                    ← Más clientes
│
├── 📁 database/
│   └── 📄 pedidos.db                 ← Una sola BD para todos
│       └── Tabla: pedidos
│           ├── id
│           ├── numero_orden
│           ├── cliente_id           ← Identifica a qué imprenta pertenece
│           ├── producto
│           ├── cantidad
│           ├── precio_total
│           └── fecha
│
├── 📁 backend/
│   └── 📁 services/
│       ├── 📄 notificador_email.py   ← Reutilizable
│       └── 📄 bot_engine.py          ← Motor genérico
│
├── 📄 bot_publiya7_completo.py       ← Bot específico Publiya7
├── 📄 bot_multicliente.py            ← Bot genérico SaaS
└── 📄 bot_multicliente_ejemplo.py    ← Ejemplo educativo
```

## 🔄 Flujo de Funcionamiento

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE USA EL BOT                        │
│                   (WhatsApp/Web/Telegram)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ¿QUÉ CLIENTE ES? (Identificación)               │
│                                                              │
│  • Por número de teléfono WhatsApp                          │
│  • Por URL del webhook (publiya7.bot.com / xyz.bot.com)     │
│  • Por código de acceso inicial                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              CARGAR CONFIGURACIÓN ESPECÍFICA                 │
│                                                              │
│  Si es Publiya7 → Carga: clientes/configs/publiya7.json     │
│  Si es XYZ      → Carga: clientes/configs/imprentaxyz.json  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BOT FUNCIONA CON ESA CONFIGURACIÓN              │
│                                                              │
│  • Productos diferentes                                      │
│  • Precios diferentes                                        │
│  • Información de contacto diferente                         │
│  • Mismo código, mismas funciones                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              GUARDAR PEDIDO EN BASE DE DATOS                 │
│                                                              │
│  INSERT INTO pedidos (cliente_id, producto, ...)            │
│  VALUES ('publiya7', 'Tarjetas', ...)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              NOTIFICAR AL CLIENTE CORRECTO                   │
│                                                              │
│  • Email a publiya7@gmail.com                               │
│  • Email a contacto@imprentaxyz.com                         │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Ventajas de esta Estructura

### 1. **Un Solo Código**
- No necesitas crear un bot nuevo para cada cliente
- Mantenimiento más fácil (arreglas una vez, funciona para todos)
- Actualizaciones simultáneas

### 2. **Configuración Flexible**
- Cada cliente tiene sus propios productos
- Precios diferentes por ciudad/región
- Información de contacto personalizada
- Horarios de atención específicos

### 3. **Base de Datos Unificada**
- Un solo archivo SQLite para todos los pedidos
- Fácil hacer reportes ("¿Cuántos pedidos totales hoy?")
- Puedes filtrar por cliente cuando necesites

### 4. **Escalable**
- Agregar nuevo cliente = Crear archivo JSON
- No requiere programar nada nuevo
- Puedes tener 10, 50 o 100 clientes con el mismo código

## 📝 Ejemplo: Diferencias entre Clientes

| Aspecto | Publiya7 (Medellín) | Imprenta XYZ (Bogotá) |
|---------|---------------------|----------------------|
| **Productos** | Tarjetas, Volantes, Sellos | Tarjetas, Banners, Stickers |
| **Precio tarjetas** | $75.000 por 1000 | $85.000 por 1000 |
| **Moneda** | COP | COP |
| **Teléfono** | +57 314 390 9874 | +57 300 123 4567 |
| **Horario** | L-V 8am-5pm | L-V 9am-6pm |
| **Entrega** | 2-5 días | 3-5 días |

## 🚀 Cómo Agregar un Nuevo Cliente

### Paso 1: Crear archivo JSON
```bash
# Copiar plantilla
# Modificar productos, precios, contacto
# Guardar como: clientes/configs/nuevocliente.json
```

### Paso 2: Configurar webhook
```
https://tubot.com/webhook/nuevocliente
```

### Paso 3: ¡Listo!
El bot automáticamente:
- Carga la configuración correcta
- Usa los precios de ese cliente
- Envía notificaciones al email correcto
- Guarda pedidos con su cliente_id

## 💰 Modelo de Negocio SaaS

Puedes cobrar a los clientes:
- **Mensualidad fija**: $X por mes
- **Por pedido**: $X por cada pedido procesado
- **Por volumen**: Planes según cantidad de pedidos
- **Setup inicial**: Cargo único por configuración

---

**¿Te gustaría que implementemos esta estructura multi-cliente en el bot actual?**
