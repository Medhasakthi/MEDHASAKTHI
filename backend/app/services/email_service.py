"""
Email service for sending notifications and verification emails
"""
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader, Template
from typing import Optional, Dict, Any
import os
from pathlib import Path

from app.core.config import settings


class EmailService:
    """Email service using SendGrid"""
    
    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY) if settings.SENDGRID_API_KEY else None
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        
        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send email using SendGrid"""
        try:
            if not self.sg:
                print(f"Email would be sent to {to_email}: {subject}")
                print(f"Content: {html_content}")
                return True  # For development without SendGrid
            
            from_email = Email(self.from_email, self.from_name)
            to_email = To(to_email)
            
            mail = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            response = self.sg.send(mail)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """Render email template with data"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            print(f"Template rendering failed: {str(e)}")
            return self._get_fallback_template(template_name, **kwargs)
    
    def _get_fallback_template(self, template_name: str, **kwargs) -> str:
        """Fallback templates when file templates are not available"""
        if template_name == "verification.html":
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">MEDHASAKTHI</h1>
                    <p style="color: white; margin: 5px 0;">AI-Powered Examination Platform</p>
                </div>
                
                <div style="padding: 30px 20px;">
                    <h2 style="color: #333;">Welcome, {kwargs.get('first_name', 'User')}!</h2>
                    
                    <p style="color: #666; line-height: 1.6;">
                        Thank you for registering with MEDHASAKTHI. To complete your registration and start using our AI-powered examination platform, please verify your email address.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{kwargs.get('verification_url', '#')}" 
                           style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Verify Email Address
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        If the button doesn't work, copy and paste this link into your browser:<br>
                        <a href="{kwargs.get('verification_url', '#')}" style="color: #667eea;">{kwargs.get('verification_url', '#')}</a>
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        This verification link will expire in 24 hours for security reasons.
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 12px; margin: 0;">
                        © 2024 MEDHASAKTHI. All rights reserved.<br>
                        If you didn't create an account, please ignore this email.
                    </p>
                </div>
            </body>
            </html>
            """
        
        elif template_name == "password_reset.html":
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">MEDHASAKTHI</h1>
                    <p style="color: white; margin: 5px 0;">Password Reset Request</p>
                </div>
                
                <div style="padding: 30px 20px;">
                    <h2 style="color: #333;">Hello, {kwargs.get('first_name', 'User')}!</h2>
                    
                    <p style="color: #666; line-height: 1.6;">
                        We received a request to reset your password for your MEDHASAKTHI account. If you made this request, click the button below to reset your password.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{kwargs.get('reset_url', '#')}" 
                           style="background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        If the button doesn't work, copy and paste this link into your browser:<br>
                        <a href="{kwargs.get('reset_url', '#')}" style="color: #dc3545;">{kwargs.get('reset_url', '#')}</a>
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        This password reset link will expire in 1 hour for security reasons.
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        <strong>If you didn't request this password reset, please ignore this email.</strong> Your password will remain unchanged.
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 12px; margin: 0;">
                        © 2024 MEDHASAKTHI. All rights reserved.<br>
                        For security reasons, this link will expire in 1 hour.
                    </p>
                </div>
            </body>
            </html>
            """
        
        elif template_name == "welcome.html":
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">MEDHASAKTHI</h1>
                    <p style="color: white; margin: 5px 0;">Welcome to the Future of Education</p>
                </div>
                
                <div style="padding: 30px 20px;">
                    <h2 style="color: #333;">Welcome aboard, {kwargs.get('first_name', 'User')}! 🎉</h2>
                    
                    <p style="color: #666; line-height: 1.6;">
                        Your email has been verified successfully! You're now ready to experience the power of AI-driven education with MEDHASAKTHI.
                    </p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #333; margin-top: 0;">What you can do now:</h3>
                        <ul style="color: #666; line-height: 1.8;">
                            <li>🎯 Take adaptive practice tests</li>
                            <li>📊 Track your performance with AI insights</li>
                            <li>🏆 Compete on leaderboards</li>
                            <li>📜 Earn verified certificates</li>
                            <li>🤖 Get personalized study recommendations</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{kwargs.get('login_url', '#')}" 
                           style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Start Learning Now
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        Need help getting started? Check out our <a href="#" style="color: #667eea;">Quick Start Guide</a> or contact our support team.
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 12px; margin: 0;">
                        © 2024 MEDHASAKTHI. All rights reserved.<br>
                        Ready to revolutionize your learning experience!
                    </p>
                </div>
            </body>
            </html>
            """
        
        return f"<html><body><h1>{template_name}</h1><p>Template not found</p></body></html>"
    
    async def send_verification_email(
        self,
        email: str,
        first_name: str,
        verification_token: str
    ) -> bool:
        """Send email verification email"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        html_content = self.render_template(
            "verification.html",
            first_name=first_name,
            verification_url=verification_url,
            verification_token=verification_token
        )
        
        return await self.send_email(
            to_email=email,
            subject="Verify Your MEDHASAKTHI Account",
            html_content=html_content
        )
    
    async def send_password_reset_email(
        self,
        email: str,
        first_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_content = self.render_template(
            "password_reset.html",
            first_name=first_name,
            reset_url=reset_url,
            reset_token=reset_token
        )
        
        return await self.send_email(
            to_email=email,
            subject="Reset Your MEDHASAKTHI Password",
            html_content=html_content
        )
    
    async def send_welcome_email(
        self,
        email: str,
        first_name: str
    ) -> bool:
        """Send welcome email after verification"""
        login_url = f"{settings.FRONTEND_URL}/login"
        
        html_content = self.render_template(
            "welcome.html",
            first_name=first_name,
            login_url=login_url
        )
        
        return await self.send_email(
            to_email=email,
            subject="Welcome to MEDHASAKTHI! 🎉",
            html_content=html_content
        )
    
    async def send_bulk_registration_email(
        self,
        email: str,
        first_name: str,
        temporary_password: str,
        institute_name: str
    ) -> bool:
        """Send email for bulk registered users"""
        login_url = f"{settings.FRONTEND_URL}/login"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">MEDHASAKTHI</h1>
                <p style="color: white; margin: 5px 0;">Your Account Has Been Created</p>
            </div>
            
            <div style="padding: 30px 20px;">
                <h2 style="color: #333;">Hello, {first_name}!</h2>
                
                <p style="color: #666; line-height: 1.6;">
                    Your account has been created by <strong>{institute_name}</strong>. You can now access the MEDHASAKTHI platform using the credentials below.
                </p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3 style="color: #333; margin-top: 0;">Your Login Credentials:</h3>
                    <p style="margin: 10px 0;"><strong>Email:</strong> {email}</p>
                    <p style="margin: 10px 0;"><strong>Temporary Password:</strong> <code style="background: #e9ecef; padding: 2px 6px; border-radius: 3px;">{temporary_password}</code></p>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; color: #856404;">
                        <strong>Important:</strong> Please change your password after your first login for security reasons.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" 
                       style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Login to Your Account
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                <p style="color: #666; font-size: 12px; margin: 0;">
                    © 2024 MEDHASAKTHI. All rights reserved.<br>
                    If you have any questions, please contact your institution administrator.
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=email,
            subject=f"Your MEDHASAKTHI Account - {institute_name}",
            html_content=html_content
        )


# Global email service instance
email_service = EmailService()
