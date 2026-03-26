-- Base de datos BotlyPro SaaS - VERSIÓN PRO
-- Estructura normalizada para escalar sin límites

-- ============================================
-- 1. TABLA: clientes
-- Información de cada negocio/cliente SaaS
-- ============================================
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT UNIQUE NOT NULL,      -- Ej: publiya7, imprenta_xyz
    
    -- Datos del negocio
    nombre TEXT NOT NULL,                 -- Nombre del negocio
    eslogan TEXT,
    nit TEXT,                             -- NIT o identificación fiscal
    
    -- Contacto
    telefono TEXT NOT NULL,               -- Teléfono principal
    whatsapp TEXT,                        -- Número WhatsApp del negocio
    email TEXT,
    direccion TEXT,
    ciudad TEXT,
    departamento TEXT,
    pais TEXT DEFAULT 'Colombia',
    
    -- Configuración del bot (JSON flexible)
    config_json TEXT,                     -- Toda la config del bot en JSON
    
    -- Estado y plan SaaS
    estado TEXT DEFAULT 'activo',         -- activo, inactivo, suspendido, trial
    plan TEXT DEFAULT 'basico',           -- basico, pro, enterprise
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actividad TIMESTAMP,
    fecha_expiracion TIMESTAMP,           -- Para trials o planes con fecha
    
    -- Notificaciones al dueño
    notificar_whatsapp BOOLEAN DEFAULT 1,
    notificar_email BOOLEAN DEFAULT 0,
    email_notificaciones TEXT,
    telefono_notificaciones TEXT,
    
    -- Metadata
    etiquetas TEXT,                       -- JSON: ["imprenta", "cliente_frecuente"]
    notas TEXT,
    
    -- Límites del plan
    limite_mensajes_mes INTEGER DEFAULT 1000,
    limite_productos INTEGER DEFAULT 50,
    limite_pedidos_mes INTEGER DEFAULT 100
);

-- ============================================
-- 2. TABLA: productos
-- Catálogo de productos por cliente (NORMALIZADO)
-- ============================================
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,
    
    -- Identificación
    prod_id TEXT NOT NULL,                -- Ej: tarjeta_sencilla, banner_1
    categoria_id TEXT NOT NULL,           -- Ej: tarjetas, gran_formato
    
    -- Información
    nombre TEXT NOT NULL,
    descripcion TEXT,
    
    -- Tipo de cotización
    tipo_cotizacion TEXT DEFAULT 'cantidad',  -- cantidad, medida, unitario, personalizado
    unidad_medida TEXT,                   -- unidad, cm2, m2, ml
    
    -- Precios (flexible según tipo)
    precio_1000 INTEGER,                  -- Precio base por 1000 unidades
    precio_2000 INTEGER,                  -- Precio con descuento 5%
    precio_5000 INTEGER,                  -- Precio con descuento 10%
    precio_unitario INTEGER,              -- Para productos unitarios
    precio_cm2 REAL,                      -- Para cotización por cm2
    precio_m2 REAL,                       -- Para cotización por m2
    
    -- Configuración
    activo BOOLEAN DEFAULT 1,
    requiere_cotizacion BOOLEAN DEFAULT 0,  -- Si necesita cotización manual
    
    -- Orden en el menú
    orden INTEGER DEFAULT 0,
    
    -- Timestamps
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE,
    UNIQUE(cliente_id, categoria_id, prod_id)
);

-- ============================================
-- 3. TABLA: carritos
-- Carritos de compra activos por usuario
-- ============================================
CREATE TABLE carritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,             -- A qué negocio pertenece
    usuario_id TEXT NOT NULL,             -- Teléfono del cliente final
    
    -- Estado
    estado TEXT DEFAULT 'activo',         -- activo, confirmado, completado, abandonado, expirado
    
    -- Totales
    subtotal INTEGER DEFAULT 0,
    descuento INTEGER DEFAULT 0,
    total INTEGER DEFAULT 0,
    cantidad_items INTEGER DEFAULT 0,
    
    -- Metadata
    notas TEXT,                           -- Notas del cliente
    fuente TEXT DEFAULT 'whatsapp',       -- whatsapp, web, etc
    
    -- Timestamps
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira_en TIMESTAMP,                  -- Carrito expira después de X tiempo (30 min)
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
    UNIQUE(cliente_id, usuario_id)
);

-- ============================================
-- 4. TABLA: carrito_items
-- Items dentro de cada carrito
-- ============================================
CREATE TABLE carrito_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carrito_id INTEGER NOT NULL,
    
    -- Producto (copiamos datos para histórico)
    producto_id INTEGER,                  -- Referencia al producto
    categoria_id TEXT,
    prod_id TEXT,
    nombre_producto TEXT,
    
    -- Cantidad/Medidas
    cantidad INTEGER,                     -- Para productos por cantidad
    medidas TEXT,                         -- Ej: "100x200cm" para productos por medida
    area INTEGER,                         -- Área calculada en cm2
    
    -- Precios
    precio_unitario INTEGER,
    subtotal INTEGER,
    
    -- Timestamp
    agregado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (carrito_id) REFERENCES carritos(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- ============================================
-- 5. TABLA: pedidos
-- Pedidos confirmados (ventas reales)
-- ============================================
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_orden TEXT UNIQUE NOT NULL,    -- Ej: ORD-20260326-1234
    
    cliente_id TEXT NOT NULL,             -- Negocio que vendió
    usuario_id TEXT NOT NULL,             -- Cliente que compró
    carrito_id INTEGER,                   -- Referencia al carrito (opcional)
    
    -- Totales
    subtotal INTEGER NOT NULL,
    descuento INTEGER DEFAULT 0,
    total INTEGER NOT NULL,
    cantidad_items INTEGER,
    
    -- Estado del pedido
    estado TEXT DEFAULT 'pendiente',      -- pendiente, confirmado, procesando, enviado, completado, cancelado
    
    -- Información del comprador
    nombre_comprador TEXT,
    telefono_contacto TEXT,
    email_contacto TEXT,
    direccion_entrega TEXT,
    ciudad_entrega TEXT,
    
    -- Información de pago
    metodo_pago TEXT,                     -- efectivo, transferencia, nequi, etc
    estado_pago TEXT DEFAULT 'pendiente', -- pendiente, pagado, parcial
    
    -- Notas
    notas_cliente TEXT,                   -- Lo que escribió el cliente
    notas_internas TEXT,                  -- Para uso interno del negocio
    
    -- Timestamps
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmado_en TIMESTAMP,
    pagado_en TIMESTAMP,
    enviado_en TIMESTAMP,
    completado_en TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
    FOREIGN KEY (carrito_id) REFERENCES carritos(id)
);

-- ============================================
-- 6. TABLA: pedido_items
-- Items de cada pedido confirmado
-- ============================================
CREATE TABLE pedido_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    
    -- Producto (copiamos para histórico)
    producto_id INTEGER,
    categoria_id TEXT,
    prod_id TEXT,
    nombre_producto TEXT,
    
    -- Cantidad/Medidas
    cantidad INTEGER,
    medidas TEXT,
    area INTEGER,
    
    -- Precios (congelados al momento del pedido)
    precio_unitario INTEGER,
    subtotal INTEGER,
    
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);

-- ============================================
-- 7. TABLA: conversaciones
-- Historial completo de conversaciones (ORO)
-- ============================================
CREATE TABLE conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,             -- Negocio
    usuario_id TEXT NOT NULL,             -- Teléfono del cliente
    
    -- Mensajes
    mensaje TEXT,                         -- Lo que escribió el usuario
    respuesta TEXT,                       -- Lo que respondió el bot
    
    -- Contexto
    tipo TEXT DEFAULT 'general',          -- saludo, cotizacion, pedido, error, menu
    intencion TEXT,                       -- Qué intentaba hacer el usuario
    
    -- Estado de la conversación
    paso INTEGER,                         -- Paso del flujo (0, 1, 2, 3...)
    categoria_seleccionada TEXT,
    producto_seleccionado TEXT,
    
    -- Metadata del bot
    modelo_ia TEXT,                       -- Si usamos IA en el futuro
    confianza REAL,                       -- Confianza de la respuesta
    
    -- Timestamp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

-- ============================================
-- 8. TABLA: estado_usuario
-- Estado actual de cada conversación (para mantener contexto)
-- ============================================
CREATE TABLE estado_usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,
    usuario_id TEXT NOT NULL,
    
    -- Estado del flujo
    paso INTEGER DEFAULT 0,               -- 0: inicio, 1: categoria, 2: producto, 3: cantidad, 4: confirmacion
    categoria TEXT,
    producto INTEGER,
    cantidad TEXT,                        -- Puede ser número o medidas (ej: "100x200")
    total INTEGER DEFAULT 0,
    
    -- Datos extra (JSON flexible)
    datos_extra TEXT,                     -- JSON con datos adicionales
    
    -- Carrito activo
    carrito_id INTEGER,
    
    -- Timestamp
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
    FOREIGN KEY (carrito_id) REFERENCES carritos(id),
    UNIQUE(cliente_id, usuario_id)
);

-- ============================================
-- 9. TABLA: metricas_cliente (VISTA/MATERIALIZADA)
-- Métricas calculadas por cliente (para dashboard)
-- ============================================
CREATE TABLE metricas_cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT UNIQUE NOT NULL,
    
    -- Métricas de ventas
    total_cotizaciones INTEGER DEFAULT 0,
    total_pedidos INTEGER DEFAULT 0,
    total_ventas INTEGER DEFAULT 0,       -- En pesos
    ticket_promedio INTEGER DEFAULT 0,
    
    -- Métricas de clientes
    clientes_unicos INTEGER DEFAULT 0,     -- Números diferentes que han escrito
    clientes_recurrentes INTEGER DEFAULT 0, -- Que han comprado más de 1 vez
    
    -- Métricas de productos
    producto_mas_vendido TEXT,
    categoria_mas_popular TEXT,
    
    -- Métricas de conversación
    total_mensajes INTEGER DEFAULT 0,
    tasa_conversion REAL DEFAULT 0,       -- % de cotizaciones que se convierten en pedidos
    
    -- Actualización
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

-- ============================================
-- 10. TABLA: notificaciones
-- Cola de notificaciones al dueño del negocio
-- ============================================
CREATE TABLE notificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,
    
    tipo TEXT NOT NULL,                   -- nuevo_pedido, cotizacion, cliente_nuevo, carrito_abandonado
    titulo TEXT,
    mensaje TEXT,
    
    -- Datos relacionados
    pedido_id INTEGER,
    usuario_id TEXT,
    
    -- Estado
    leida BOOLEAN DEFAULT 0,
    enviada BOOLEAN DEFAULT 0,
    
    -- Canales
    canal_whatsapp BOOLEAN DEFAULT 1,
    canal_email BOOLEAN DEFAULT 0,
    
    -- Timestamps
    creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    enviada_en TIMESTAMP,
    leida_en TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

-- ============================================
-- ÍNDICES para optimización
-- ============================================
CREATE INDEX idx_clientes_estado ON clientes(estado);
CREATE INDEX idx_clientes_plan ON clientes(plan);
CREATE INDEX idx_productos_cliente ON productos(cliente_id, activo);
CREATE INDEX idx_productos_categoria ON productos(cliente_id, categoria_id);
CREATE INDEX idx_carritos_estado ON carritos(estado);
CREATE INDEX idx_carritos_expira ON carritos(expira_en);
CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_id, estado);
CREATE INDEX idx_pedidos_fecha ON pedidos(creado_en);
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_conversaciones_cliente ON conversaciones(cliente_id, usuario_id);
CREATE INDEX idx_conversaciones_fecha ON conversaciones(timestamp);
CREATE INDEX idx_notificaciones_cliente ON notificaciones(cliente_id, leida);

-- ============================================
-- DATOS INICIALES
-- ============================================

-- Cliente de ejemplo: Publiya7
INSERT INTO clientes (
    cliente_id, nombre, eslogan, telefono, whatsapp, email,
    ciudad, departamento, direccion,
    estado, plan, etiquetas
) VALUES (
    'publiya7',
    'Publiya7',
    'Publicidad al Instante',
    '+57 314 390 9874',
    '+57 314 390 9874',
    'publiya7@gmail.com',
    'Medellín',
    'Antioquia',
    'Medellín, Colombia',
    'activo',
    'pro',
    '["imprenta", "cliente_inicial"]'
);

-- Productos de ejemplo para Publiya7
INSERT INTO productos (cliente_id, categoria_id, prod_id, nombre, descripcion, tipo_cotizacion, precio_1000, precio_2000, precio_5000) VALUES
('publiya7', 'tarjetas', 'sencilla_uv', 'Sencilla Brillo UV', 'Tarjeta sencilla 1 cara', 'cantidad', 75000, 142500, 337500),
('publiya7', 'tarjetas', 'mate', 'Mate Premium', 'Tarjeta mate 2 caras', 'cantidad', 119000, 226100, 535500);
