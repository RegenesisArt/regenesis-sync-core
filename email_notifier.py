"""
Email notification system
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailNotifier:
    def __init__(self):
        # Use Gmail SMTP (free)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_USER", "")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD", "")
        
    def send_email(self, to_email, subject, body, html_body=None):
        """Send email notification"""
        if not self.sender_email or not self.sender_password:
            print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            return {"status": "mock", "reason": "no_credentials"}
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[CMHP] {subject}"
            msg["From"] = self.sender_email
            msg["To"] = to_email
            
            # Attach both plain and HTML
            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            
            # Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}: {subject}")
            return {"status": "sent", "to": to_email}
            
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def send_health_alert(self, health_data):
        """Send health alert email"""
        subject = "Health Alert"
        body = f"""
CMHP Health Alert:
- Temperature: {health_data.get('temperature', 'N/A')}°F
- Sleep: {health_data.get('sleep_hours', 'N/A')} hours
- Energy: {health_data.get('energy', 'N/A')}/10
- Time: {health_data.get('timestamp', 'N/A')}
"""
        return self.send_email(
            to_email=self.sender_email,  # Send to yourself
            subject=subject,
            body=body
        )
    
    def send_sale_notification(self, sale_data):
        """Send sale notification"""
        subject = f"🎨 SALE! ${sale_data.get('amount', 0)}"
        body = f"""
CONGRATULATIONS! You made a sale!

Details:
- Amount: ${sale_data.get('amount', 0)}
- Item: {sale_data.get('item', 'Unknown')}
- Buyer: {sale_data.get('buyer', 'Unknown')}
- Date: {sale_data.get('date', 'N/A')}

The Key Progress: ${sale_data.get('the_key_progress', 0)}/$6,000
"""
        return self.send_email(
            to_email=self.sender_email,
            subject=subject,
            body=body
        )

# Global instance
emailer = EmailNotifier()
