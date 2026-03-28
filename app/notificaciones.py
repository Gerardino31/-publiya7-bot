"""
notificaciones.py - Sistema de notificaciones para nuevos pedidos
Envía alertas al dueño del negocio vía Email (Gmail SMTP o SendGrid)
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from datetime import datetime

# Intentar importar SendGrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("⚠️ SendGrid no instalado. Ejecuta: pip install sendgrid")


class NotificadorPedidos:
    """Envía notificaciones cuando hay pedidos nuevos"""

    def __init__(self):
        # Configuración SendGrid
        self.sendgrid_key = os.getenv('SENDGRID_API_KEY')
        self.email_from = os.getenv('EMAIL_FROM', 'pedidos@botlypro.com')

        # Configuración Gmail SMTP
        self.gmail_user = os.getenv('GMAIL_USER', '')  # ej: publiya7@gmail.com
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD', '')  # Contraseña de aplicación
        self.use_gmail = bool(self.gmail_user and self.gmail_password)

        # Inicializar cliente SendGrid si hay API key
        if SENDGRID_AVAILABLE and self.sendgrid_key:
            self.sg = SendGridAPIClient(self.sendgrid_key)
            print("✅ SendGrid configurado")
        else:
            self.sg = None
            if not SENDGRID_AVAILABLE:
                print("⚠️ SendGrid no disponible")
            if not self.sendgrid_key:
                print("⚠️ SENDGRID_API_KEY no configurada")

        # Verificar Gmail SMTP
        if self.use_gmail:
            print(f"✅ Gmail SMTP configurado: {self.gmail_user}")
        else:
            print("⚠️ Gmail SMTP no configurado (GMAIL_USER o GMAIL_APP_PASSWORD faltan)")

    def notificar_nuevo_pedido(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> bool:
        """
        Envía notificación de nuevo pedido al dueño del negocio
        
        Args:
            cliente_config: Configuración del cliente (negocio)
            pedido: Datos del pedido
            items: Items del pedido
        """
        # NOTA: Email desactivado en Render gratis (SMTP bloqueado)
        # Solo notificaciones por WhatsApp por ahora
        print("ℹ️ Notificaciones por email desactivadas (Render free tier)")
        print("✅ Pedido guardado correctamente")
        return True

    def _notificar_email(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> bool:
        """Envía notificación por Email usando SendGrid o Gmail SMTP"""
        email_destino = cliente_config.get('email_notificaciones') or cliente_config.get('email')
        if not email_destino:
            print("⚠️ No hay email configurado para notificaciones")
            return False

        # Intentar primero con Gmail SMTP si está configurado
        if self.use_gmail:
            return self._enviar_email_gmail(cliente_config, pedido, items, email_destino)

        # Si no hay Gmail, intentar con SendGrid
        if self.sg:
            return self._enviar_email_sendgrid(cliente_config, pedido, items, email_destino)

        print("⚠️ Ni Gmail ni SendGrid están configurados")
        return False

    def _enviar_email_gmail(self, cliente_config: Dict, pedido: Dict, items: List[Dict], email_destino: str) -> bool:
        """Envía email usando Gmail SMTP"""
        try:
            # Construir el email
            mensaje_html = self._construir_email_html(cliente_config, pedido, items)

            # Crear mensaje MIME
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🛒 Nuevo Pedido #{pedido.get('numero_orden')} - {cliente_config.get('nombre', 'Tu Negocio')}"
            msg['From'] = self.gmail_user
            msg['To'] = email_destino

            # Adjuntar contenido HTML
            part = MIMEText(mensaje_html, 'html')
            msg.attach(part)

            # Conectar a Gmail SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.sendmail(self.gmail_user, email_destino, msg.as_string())

            print(f"✅ Email enviado via Gmail a {email_destino}")
            return True

        except Exception as e:
            print(f"❌ Error enviando email via Gmail: {e}")
            return False

    def _enviar_email_sendgrid(self, cliente_config: Dict, pedido: Dict, items: List[Dict], email_destino: str) -> bool:
        """Envía email usando SendGrid"""
        try:
            # Construir el email
            mensaje_html = self._construir_email_html(cliente_config, pedido, items)
            mensaje_texto = self._construir_email_texto(cliente_config, pedido, items)

            # Crear el email
            message = Mail(
                from_email=Email(self.email_from, "BotlyPro - Pedidos"),
                to_emails=To(email_destino),
                subject=f"🛒 Nuevo Pedido #{pedido.get('numero_orden')} - {cliente_config.get('nombre', 'Tu Negocio')}",
                html_content=mensaje_html,
                plain_text_content=mensaje_texto
            )

            # Enviar
            response = self.sg.send(message)

            if response.status_code in [200, 201, 202]:
                print(f"✅ Email enviado via SendGrid a {email_destino}: {response.status_code}")
                return True
            else:
                print(f"⚠️ Error enviando email via SendGrid: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error enviando email via SendGrid: {e}")
            return False

    def _construir_email_html(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> str:
        """Construye el cuerpo del email en HTML"""
        nombre_negocio = cliente_config.get('nombre', 'Tu negocio')
        numero_orden = pedido.get('numero_orden', 'N/A')
        total = pedido.get('total', 0)

        # Construir tabla de productos
        productos_html = ""
        for item in items:
            if item.get('medidas'):
                cantidad = item['medidas']
            else:
                cantidad = f"{item.get('cantidad', 0):,} unid"

            productos_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.get('nombre_producto', 'Producto')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{cantidad}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${item.get('subtotal', 0):,} COP</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Nuevo Pedido - {nombre_negocio}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0;">🛒 ¡Nuevo Pedido Recibido!</h1>
                </div>

                <div style="background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none;">
                    <h2 style="color: #667eea; margin-top: 0;">{nombre_negocio}</h2>

                    <div style="background: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>📦 Número de Orden:</strong> #{numero_orden}</p>
                        <p style="margin: 5px 0;"><strong>📅 Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                        <p style="margin: 5px 0; font-size: 18px; color: #48bb78;">
                            <strong>💰 Total: ${total:,} COP</strong>
                        </p>
                    </div>

                    <h3 style="color: #667eea;">📋 Productos:</h3>
                    <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 5px;">
                        <thead>
                            <tr style="background: #667eea; color: white;">
                                <th style="padding: 10px; text-align: left;">Producto</th>
                                <th style="padding: 10px; text-align: center;">Cantidad</th>
                                <th style="padding: 10px; text-align: right;">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {productos_html}
                        </tbody>
                    </table>

                    <div style="background: #e6fffa; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #38b2ac;">
                        <h4 style="margin-top: 0; color: #234e52;">📱 Datos del Cliente:</h4>
                        <p style="margin: 5px 0;"><strong>Teléfono:</strong> {pedido.get('usuario_id', 'N/A')}</p>
                        {f"<p style='margin: 5px 0;'><strong>Nombre:</strong> {pedido.get('nombre_comprador')}</p>" if pedido.get('nombre_comprador') else ""}
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://publiya7-bot.onrender.com/admin"
                           style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Ver en Panel Admin
                        </a>
                    </div>
                </div>

                <div style="text-align: center; padding: 20px; color: #718096; font-size: 12px;">
                    <p>Este pedido fue generado automáticamente por BotlyPro</p>
                    <p>© 2024 BotlyPro - Todos los derechos reservados</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _construir_email_texto(self, cliente_config: Dict, pedido: Dict, items: List[Dict]) -> str:
        """Construye el cuerpo del email en texto plano (fallback)"""
        nombre_negocio = cliente_config.get('nombre', 'Tu negocio')

        texto = f"""🛒 ¡NUEVO PEDIDO RECIBIDO!

{nombre_negocio}

📦 Número de Orden: #{pedido.get('numero_orden', 'N/A')}
📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
💰 Total: ${pedido.get('total', 0):,} COP

📋 PRODUCTOS:
"""

        for item in items:
            if item.get('medidas'):
                cantidad = item['medidas']
            else:
                cantidad = f"{item.get('cantidad', 0):,} unid"

            texto += f"\n• {item.get('nombre_producto')}: {cantidad} = ${item.get('subtotal', 0):,} COP"

        texto += f"""

📱 DATOS DEL CLIENTE:
Teléfono: {pedido.get('usuario_id', 'N/A')}
{f"Nombre: {pedido.get('nombre_comprador')}" if pedido.get('nombre_comprador') else ""}

Ver pedido en: https://publiya7-bot.onrender.com/admin

---
Este pedido fue generado automáticamente por BotlyPro
"""

        return texto


# Instancia global
notificador = NotificadorPedidos()
