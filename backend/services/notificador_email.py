# Módulo de notificaciones por email
# Para enviar correos cuando se confirma un pedido

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class NotificadorEmail:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        # Nota: En producción, estas credenciales deben estar en variables de entorno
        self.email_origen = "publiya7@gmail.com"  # Email de la empresa
        self.email_destino = "publiya7@gmail.com"  # Mismo email para recibir notificaciones
    
    def enviar_notificacion_pedido(self, pedido: dict) -> bool:
        """
        Envía un email de notificación cuando se confirma un pedido.
        
        Args:
            pedido: Diccionario con los datos del pedido
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.email_origen
            msg['To'] = self.email_destino
            msg['Subject'] = f"🛒 Nuevo Pedido Confirmado - {pedido['numero_orden']}"
            
            # Cuerpo del email
            cuerpo = self._generar_cuerpo_email(pedido)
            msg.attach(MIMEText(cuerpo, 'html'))
            
            # En producción, aquí se conectaría al servidor SMTP
            # Por ahora, solo simulamos el envío
            print(f"\n{'='*60}")
            print("📧 EMAIL DE NOTIFICACIÓN ENVIADO")
            print(f"{'='*60}")
            print(f"Para: {self.email_destino}")
            print(f"Asunto: {msg['Subject']}")
            print(f"\n{cuerpo}")
            print(f"{'='*60}\n")
            
            # Nota: Para envío real, descomentar:
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.email_origen, password)
            # server.send_message(msg)
            # server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error al enviar email: {e}")
            return False
    
    def _generar_cuerpo_email(self, pedido: dict) -> str:
        """Genera el cuerpo HTML del email."""
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2c5aa0;">🛒 Nuevo Pedido Confirmado</h2>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c5aa0;">📋 Detalles del Pedido</h3>
                    <p><strong>Número de Orden:</strong> {pedido['numero_orden']}</p>
                    <p><strong>Fecha:</strong> {fecha}</p>
                    <p><strong>Estado:</strong> 🆕 Nuevo</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #2c5aa0;">📦 Producto</h3>
                    <p><strong>Producto:</strong> {pedido['producto']}</p>
                    <p><strong>Tipo:</strong> {pedido.get('tipo', 'N/A')}</p>
                    <p><strong>Cantidad/Medidas:</strong> {pedido['cantidad']}</p>
                </div>
                
                <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2e7d32;">💰 Precio</h3>
                    <p style="font-size: 24px; font-weight: bold; color: #2e7d32; margin: 10px 0;">
                        ${pedido['precio_total']:,} COP
                    </p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #2c5aa0;">📝 Notas</h3>
                    <p>{pedido.get('notas', 'Sin notas adicionales')}</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666; text-align: center;">
                    Este es un mensaje automático del sistema de pedidos de Publiya7.<br>
                    Por favor, no responda a este email.
                </p>
            </div>
        </body>
        </html>
        """


# Prueba
if __name__ == "__main__":
    notificador = NotificadorEmail()
    
    pedido_prueba = {
        'numero_orden': 'ORD-20260321-0001',
        'producto': 'Tarjetas de Presentación',
        'tipo': 'Mate 2 caras',
        'cantidad': '5000',
        'precio_total': 650000,
        'notas': 'Cliente solicita diseño profesional'
    }
    
    notificador.enviar_notificacion_pedido(pedido_prueba)
