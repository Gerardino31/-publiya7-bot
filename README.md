# Bot WhatsApp - Publiya7

Sistema de chatbot multi-cliente para imprentas, con integración WhatsApp Business API.

## 🚀 Características

- ✅ Multi-cliente SaaS
- ✅ Detección automática por número WhatsApp
- ✅ Autenticación por código de acceso
- ✅ Persistencia de estado en BD
- ✅ Logging profesional
- ✅ Backup automático
- ✅ Validación de webhooks

## 📋 Requisitos

- Python 3.8+
- WhatsApp Business API (Meta)
- Número de teléfono verificado

## 🔧 Instalación

### 1. Clonar repositorio
```bash
git clone <url-del-repo>
cd automatizacion-mensajeria
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 4. Registrar clientes
```bash
python registrar_clientes.py
```

### 5. Iniciar el bot
```bash
# Desarrollo
python main.py

# Producción con PM2
pm2 start ecosystem.config.json
```

## ⚙️ Configuración

### Variables de entorno (.env)

```env
WHATSAPP_ACCESS_TOKEN=tu_token_aqui
WHATSAPP_PHONE_NUMBER_ID=tu_phone_id_aqui
WHATSAPP_VERIFY_TOKEN=tu_verify_token_aqui
DATABASE_PATH=database/pedidos.db
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### Registrar nuevo cliente

1. Crear archivo JSON en `clientes/configs/`
2. Ejecutar `python registrar_clientes.py`
3. Asignar código de acceso e identificador

## 📁 Estructura

```
automatizacion-mensajeria/
├── app/                    # Código fuente
│   ├── bot_autodetect.py  # Bot con auto-detección
│   ├── router.py          # Lógica de mensajes
│   ├── loader.py          # Carga de configs
│   └── config.py          # Configuración
├── clientes/
│   └── configs/           # JSONs por cliente
├── database/              # Base de datos SQLite
├── backups/              # Backups automáticos
├── logs/                 # Logs del sistema
├── .env                  # Variables de entorno
└── main.py              # Punto de entrada
```

## 🔒 Seguridad

- NUNCA subir `.env` a Git
- Rotar tokens periódicamente
- Hacer backup diario de la BD
- Usar HTTPS en producción

## 📝 Comandos útiles

```bash
# Backup manual
python backup.py

# Ver logs
tail -f logs/app.log

# PM2
pm2 status
pm2 logs bot-publiya7
pm2 restart bot-publiya7
```

## 🆘 Soporte

Para soporte contactar: publiya7@gmail.com
