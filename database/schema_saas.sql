-- Base de datos BotlyPro SaaS - VERSIÓN PRO IMPLEMENTABLE
-- Estructura lista para producción

-- ============================================
-- 1. TABLA: clientes
-- ============================================
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    eslogan TEXT,
    telefono TEXT NOT NULL,
    whatsapp TEXT,
    email TEXT,
    direccion TEXT,
    ciudad TEXT,
    departamento TEXT,
    pais TEXT DEFAULT 'Colombia',
    config_json TEXT,
    estado TEXT DEFAULT 'activo',
    plan TEXT DEFAULT 'basico',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultima_actividad TIMESTAMP
);

-- ============================================
-- 2. TABLA: productos
-- ============================================
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,
    categoria_id TEXT NOT NULL,
    prod_id TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    tipo_cotizacion TEXT DEFAULT 'cantidad',
    precio_1000 INTEGER,
    precio_2000 INTEGER,
    precio_5000 INTEGER,
    precio_unitario INTEGER,
    precio_cm2 REAL,
    activo INTEGER DEFAULT 1,
    orden INTEGER DEFAULT 0,
    UNIQUE(cliente_id, categoria_id, prod_id)
);

-- ============================================
-- 3. TABLA: carritos
-- ============================================
CREATE TABLE IF NOT EXISTS carritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,
    usuario_id TEXT NOT NULL,
    estado TEXT DEFAULT 'activo',
    total INTEGER DEFAULT 0,
    cantidad_items INTEGER DEFAULT 0,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira_en TIMESTAMP
);

-- ============================================
-- 4. TABLA: carrito_items
-- ============================================
CREATE TABLE IF NOT EXISTS carrito_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carrito_id INTEGER NOT NULL,
    categoria_id TEXT,
    prod_id TEXT,
    nombre_producto TEXT,
    cantidad INTEGER,
    medidas TEXT,
    area INTEGER,
    precio_unitario INTEGER,
    subtotal INTEGER,
    agregado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. TABLA: pedidos
-- ============================================
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_orden TEXT UNIQUE NOT NULL,
    cliente_id TEXT NOT NULL,
    usuario_id TEXT NOT NULL,
    carrito_id INTEGER,
    total INTEGER NOT NULL,
    cantidad_items INTEGER,
    estado TEXT DEFAULT 'confirmado',
    nombre_comprador TEXT,
    telefono_contacto TEXT,
    direccion_entrega TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmado_en TIMESTAMP
);

-- ============================================
-- 6. TABLA: pedido_items
-- ============================================
CREATE TABLE IF NOT EXISTS pedido_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    categoria_id TEXT,
    prod_id TEXT,
    nombre_producto TEXT,
    cantidad INTEGER,
    medidas TEXT,
    area INTEGER,
    precio_unitario INTEGER,
    subtotal INTEGER
);

-- ============================================
-- 7. TABLA: conversaciones
-- ============================================
CREATE TABLE IF NOT EXISTS conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id TEXT NOT NULL,
    usuario_id TEXT NOT NULL,
    mensaje TEXT,
    respuesta TEXT,
    tipo TEXT DEFAULT 'general',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_carritos_cliente ON carritos(cliente_id, usuario_id, estado);
CREATE INDEX IF NOT EXISTS idx_carrito_items ON carrito_items(carrito_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos(cliente_id, estado);
CREATE INDEX IF NOT EXISTS idx_conversaciones ON conversaciones(cliente_id, usuario_id);
