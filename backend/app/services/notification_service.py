import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.email_provider = settings.EMAIL_PROVIDER
        self.from_email = settings.FROM_EMAIL
        
        # SMTP configuration
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email using free SMTP or local logging"""
        try:
            if self.email_provider == "local":
                return await self._send_local_email(to_email, subject, body, html_body)
            elif self.email_provider == "smtp":
                return await self._send_smtp_email(to_email, subject, body, html_body)
            else:
                # Log email instead of sending
                return await self._log_email(to_email, subject, body, html_body)
                
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def _send_local_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email using local SMTP server"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add text and HTML parts
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Send using aiosmtplib
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Local email sending failed: {e}")
            return False
    
    async def _send_smtp_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email using external SMTP server"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add text and HTML parts
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Send using aiosmtplib
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"SMTP email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP email sending failed: {e}")
            return False
    
    async def _log_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Log email instead of sending (for development)"""
        logger.info(f"EMAIL LOGGED (not sent):")
        logger.info(f"  To: {to_email}")
        logger.info(f"  Subject: {subject}")
        logger.info(f"  Body: {body}")
        if html_body:
            logger.info(f"  HTML Body: {html_body}")
        
        return True
    
    async def send_welcome_email(self, user_email: str, username: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to AI Chatbot!"
        body = f"""
        Hello {username}!
        
        Welcome to our AI Chatbot platform. We're excited to have you on board!
        
        You can now:
        - Start conversations with our AI assistant
        - Search through our knowledge base
        - Get help with your questions
        
        If you have any questions, feel free to reach out to our support team.
        
        Best regards,
        The AI Chatbot Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to AI Chatbot!</h2>
            <p>Hello {username}!</p>
            <p>Welcome to our AI Chatbot platform. We're excited to have you on board!</p>
            <h3>You can now:</h3>
            <ul>
                <li>Start conversations with our AI assistant</li>
                <li>Search through our knowledge base</li>
                <li>Get help with your questions</li>
            </ul>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Best regards,<br>The AI Chatbot Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, body, html_body)
    
    async def send_password_reset_email(self, user_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        subject = "Password Reset Request"
        body = f"""
        Hello!
        
        You have requested a password reset for your AI Chatbot account.
        
        To reset your password, please click on the following link:
        http://localhost:3000/reset-password?token={reset_token}
        
        If you didn't request this reset, please ignore this email.
        
        This link will expire in 1 hour.
        
        Best regards,
        The AI Chatbot Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello!</p>
            <p>You have requested a password reset for your AI Chatbot account.</p>
            <p>To reset your password, please click on the following link:</p>
            <p><a href="http://localhost:3000/reset-password?token={reset_token}">Reset Password</a></p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
            <p>Best regards,<br>The AI Chatbot Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, body, html_body)
    
    async def send_notification_email(self, user_email: str, subject: str, message: str) -> bool:
        """Send general notification email"""
        body = f"""
        {message}
        
        Best regards,
        The AI Chatbot Team
        """
        
        html_body = f"""
        <html>
        <body>
            <p>{message}</p>
            <p>Best regards,<br>The AI Chatbot Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, body, html_body) 