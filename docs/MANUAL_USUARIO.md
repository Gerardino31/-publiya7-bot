# 📘 Manual de Usuario - BotlyPro

## Bot WhatsApp para Publiya7

---

## 📋 Contenido

1. [¿Qué es BotlyPro?](#qué-es-botlypro)
2. [Cómo usar el Bot (Clientes)](#cómo-usar-el-bot-clientes)
3. [Panel de Administración](#panel-de-administración)
4. [Modo Humano (Asesor)](#modo-humano-asesor)
5. [Verificación de Pagos](#verificación-de-pagos)
6. [Exportar Datos](#exportar-datos)
7. [Solución de Problemas](#solución-de-problemas)

---

## 🤖 ¿Qué es BotlyPro?

BotlyPro es un sistema de atención al cliente automatizado por WhatsApp que permite a tus clientes:

- ✅ Ver tu catálogo de productos
- ✅ Cotizar productos automáticamente
- ✅ Hacer pedidos 24/7
- ✅ Recibir confirmaciones de pedido
- ✅ Enviar comprobantes de pago

Y a ti te permite:
- 📊 Ver todos los pedidos en tiempo real
- 👥 Atender clientes personalmente (modo humano)
- 💳 Verificar pagos de clientes
- 📈 Exportar reportes de ventas

---

## 💬 Cómo usar el Bot (Clientes)

### Primer contacto

Cuando un cliente escribe por primera vez al bot, recibe el menú principal:

```
👋 ¡Buenos días! ¡Bienvenido a Publiya7!

Publicidad al Instante

¿En que podemos ayudarte?
1️⃣ Tarjetas de Presentación
2️⃣ Volantes y Plegables
3️⃣ Etiquetas
4️⃣ Cajas
5️⃣ Gran Formato
6️⃣ Sellos Automáticos
7️⃣ Otros - Por Medida
8️⃣ Otros - Precio Fijo
9️⃣ Otros - Cotización Personalizada

🎯 Escribe el número de la categoría que necesites
💡 También puedes escribir el nombre directamente
👥 Escribe ASESOR para hablar con una persona
🏠 Escribe menu en cualquier momento para volver aquí
```

### Hacer un pedido

**Paso 1:** Escribir el número de la categoría (ej: `1` para Tarjetas)

**Paso 2:** Escribir el número del producto (ej: `2` para "Mate - 2 caras")

**Paso 3:** Escribir la cantidad (ej: `1000`)

**Paso 4:** El bot muestra:
- Precio normal
- Descuento aplicado (si aplica)
- Precio final
- Ahorro

**Paso 5:** Escribir `3` para FINALIZAR pedido

**Paso 6:** Escribir `1` para confirmar

**Paso 7:** El bot envía:
```
🎉 ¡PEDIDO CONFIRMADO!
📦 Número de orden: ORD-20260328-0001
💰 Total: $156,000 COP

Métodos de pago:
📱 Nequi/Daviplata: +57 314 390 9874
💵 Efectivo: Contra entrega

📸 Envía el comprobante de pago respondiendo a este mensaje
```

### Enviar comprobante de pago

El cliente solo debe **responder con una imagen** al mensaje del bot.

El bot confirmará:
```
✅ Comprobante recibido.

⏳ Verificando pago...

Te notificaremos cuando sea confirmado.
```

---

## 🖥️ Panel de Administración

### Acceder al panel

1. Ir a: `https://publiya7-bot.onrender.com/admin/cliente-login`
2. Usuario: `publiya7`
3. Contraseña: `publiya72024`

### Dashboard

Al entrar verás:
- 💰 **Ventas Totales**: Dinero total vendido
- 📦 **Total Pedidos**: Cantidad de pedidos
- 🧾 **Ticket Promedio**: Promedio por pedido
- 👥 **Clientes Únicos**: Personas diferentes que compraron

### Ver Pedidos

Click en **"📦 Ver Pedidos"** para ver:
- Número de orden
- Cliente (teléfono)
- Total
- Estado (Pendiente, Confirmado, Completado, Cancelado)
- Fecha

### Cambiar estado de pedido

1. Click en el número de orden
2. Seleccionar nuevo estado del dropdown
3. Click "Actualizar Estado"

---

## 👥 Modo Humano (Asesor)

### ¿Qué es?

El **Modo Humano** permite que un asesor real tome el control de la conversación cuando el cliente lo solicita.

### Cómo se activa

El cliente escribe: `asesor`, `humano`, `ayuda` o `persona`

El bot responde:
```
👋 Entendido. Te conecto con un asesor.

⏸️ El bot se ha pausado temporalmente para esta conversación.

📩 Un asesor te responderá pronto. Por favor espera...
```

### Ver conversaciones activas

1. En el dashboard, click en **"👥 Modo Humano"**
2. Verás lista de clientes esperando:
   - Teléfono del cliente
   - Tiempo de espera
   - Botón "💬 Responder"

### Responder a un cliente

1. Click en **"💬 Responder"**
2. Escribe tu mensaje
3. Click **"📤 Enviar Mensaje"**
4. El cliente recibe tu mensaje en WhatsApp

### Reactivar el bot

**Opción 1 - Desde el panel:**
1. Click en **"🤖 Reactivar Bot"**

**Opción 2 - Cliente escribe:**
- `bot`
- `menu`
- `terminar`
- `listo`

El bot se reactiva automáticamente.

---

## 💳 Verificación de Pagos

### Ver pagos pendientes

1. En el dashboard, click en **"💳 Pagos Pendientes"**
2. Verás lista de comprobantes enviados:
   - Número de pedido
   - Teléfono del cliente
   - Fecha de envío
   - Botón "✅ Verificar"

### Ver detalle del comprobante

1. Click en **"✅ Verificar"**
2. Verás:
   - Información del pedido
   - Botón **"📸 Ver Comprobante"** (abre la imagen)
   - Botones para Aprobar o Rechazar

### Aprobar pago

1. Revisa la imagen del comprobante
2. Click en **"✅ Aprobar Pago"**
3. El cliente recibe automáticamente en WhatsApp:
```
✅ ¡Pago aprobado!

Tu pedido ORD-20260328-0001 está confirmado.

Pronto comenzaremos con la producción. 🚀

¿Tienes alguna pregunta? Escribe ASESOR para hablar con nosotros.
```

### Rechazar pago

1. Click en **"❌ Rechazar"**
2. El pago se marca como rechazado
3. Contacta al cliente para explicar el motivo

---

## 📊 Exportar Datos

### Exportar ventas a Excel

1. En el dashboard, click en **"📊 Exportar Mis Ventas"**
2. Se descarga archivo CSV con:
   - Número de orden
   - Comprador
   - Teléfono
   - Total
   - Estado
   - Fecha

### Usar el Excel

- Abrir con Excel o Google Sheets
- Filtrar por fecha
- Filtrar por estado
- Crear gráficos de ventas

---

## 🔧 Solución de Problemas

### El bot no responde

1. Verificar que el servicio esté activo en Render
2. Verificar que Twilio esté configurado correctamente
3. Escribir `menu` para reiniciar la conversación

### No llegan los pedidos al panel

1. Verificar que la base de datos esté funcionando
2. Revisar logs en Render
3. Contactar soporte técnico

### No puedo entrar al panel

1. Verificar usuario: `publiya7`
2. Verificar contraseña: `publiya72024`
3. Si olvidaste la contraseña, contactar a BotlyPro

### El modo humano no funciona

1. Verificar que el cliente haya escrito `asesor`
2. Refrescar la página del panel
3. Esperar 1-2 minutos y revisar de nuevo

---

## 📞 Soporte

¿Necesitas ayuda adicional?

- 📧 Email: soporte@botlypro.com
- 📱 WhatsApp: +57 314 390 9874

---

**Última actualización:** 28 de marzo de 2026  
**Versión:** BotlyPro v2.0
