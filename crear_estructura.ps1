# Comandos para crear la estructura SaaS
# Ejecutar en PowerShell

# Crear carpetas principales
New-Item -ItemType Directory -Force -Path "backend\routes"
New-Item -ItemType Directory -Force -Path "backend\services"
New-Item -ItemType Directory -Force -Path "backend\models"
New-Item -ItemType Directory -Force -Path "backend\utils"
New-Item -ItemType Directory -Force -Path "clientes\configs"
New-Item -ItemType Directory -Force -Path "clientes\data"
New-Item -ItemType Directory -Force -Path "webhooks"
New-Item -ItemType Directory -Force -Path "database\migrations"
New-Item -ItemType Directory -Force -Path "tests\unit"
New-Item -ItemType Directory -Force -Path "tests\integration"
New-Item -ItemType Directory -Force -Path "docs"

# Verificar estructura
tree /F
