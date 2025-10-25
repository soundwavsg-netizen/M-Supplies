import os
import logging
from typing import Optional
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.admin_email = "msuppliessg@gmail.com"
        # Use admin email as sender since domain verification is required for custom domains
        self.from_email = "msuppliessg@gmail.com"
        self.reply_to_email = "msuppliessg@gmail.com"
        
        if not self.api_key:
            logger.warning("SendGrid API key not configured - emails will not be sent")

    async def send_contact_form_notification(
        self,
        name: str,
        email: str,
        message: str
    ) -> bool:
        """Send contact form notification to admin"""
        
        if not self.api_key:
            logger.warning("Cannot send email - SendGrid API key not configured")
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # HTML email body for admin notification
            html_body = f"""
<h2 style="color:#f75e7a;font-family:'Poppins',sans-serif;">📬 New Contact Enquiry Received</h2>
<table style="border-collapse:collapse;font-size:14px;">
  <tr><td>👤 Name:</td><td>{name}</td></tr>
  <tr><td>📧 Email:</td><td>{email}</td></tr>
  <tr><td>💬 Message:</td><td>{message}</td></tr>
  <tr><td>🕒 Submitted At:</td><td>{timestamp}</td></tr>
</table>
<hr/>
<p style="font-size:12px;color:#999;">This email was sent automatically from the M Supplies Contact form.</p>
"""
            
            # Plain text version
            text_body = f"""
📬 New Contact Enquiry Received

👤 Name: {name}
📧 Email: {email}
💬 Message: {message}
🕒 Submitted At: {timestamp}

This email was sent automatically from the M Supplies Contact form.
"""
            
            mail = Mail(
                from_email=Email(self.from_email, "M Supplies Contact Form"),
                to_emails=To(self.admin_email),
                subject="📬 New Contact Form Message – M Supplies Website",
                plain_text_content=Content("text/plain", text_body),
                html_content=Content("text/html", html_body)
            )
            
            # Set reply-to for easy response
            mail.reply_to = Email(email, name)
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            response = sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                logger.info(f"Contact form notification sent to {self.admin_email}")
                return True
            else:
                logger.error(f"Failed to send contact notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending contact form notification: {str(e)}")
            return False

    async def send_signup_notification(
        self,
        display_name: str,
        email: str,
        phone: Optional[str] = None
    ) -> bool:
        """Send new user signup notification to admin"""
        
        if not self.api_key:
            logger.warning("Cannot send email - SendGrid API key not configured")
            return False
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # HTML email body for admin notification
            html_body = f"""
<h2 style="color:#f75e7a;font-family:'Poppins',sans-serif;">🎉 New Customer Signup!</h2>
<p>A new customer has joined <strong>M Supplies</strong>.</p>
<table style="border-collapse:collapse;font-size:14px;">
  <tr><td>👤 Name:</td><td>{display_name}</td></tr>
  <tr><td>📧 Email:</td><td>{email}</td></tr>
  <tr><td>📱 Phone:</td><td>{phone or 'Not provided'}</td></tr>
  <tr><td>🕒 Signup Time:</td><td>{timestamp}</td></tr>
</table>
<p>View this customer: <a href="https://www.msupplies.sg/admin/customers" target="_blank">Open Admin Panel</a></p>
<hr/>
<p style="font-size:12px;color:#999;">Automated email from M Supplies (INT) Pte Ltd.</p>
"""
            
            # Plain text version
            text_body = f"""
🎉 New Customer Signup!

A new customer has joined M Supplies.

👤 Name: {display_name}
📧 Email: {email}
📱 Phone: {phone or 'Not provided'}
🕒 Signup Time: {timestamp}

View this customer: https://www.msupplies.sg/admin/customers

Automated email from M Supplies (INT) Pte Ltd.
"""
            
            mail = Mail(
                from_email=Email(self.from_email, "M Supplies Website"),
                to_emails=To(self.admin_email),
                subject="🎉 New Customer Signup – M Supplies Website",
                plain_text_content=Content("text/plain", text_body),
                html_content=Content("text/html", html_body)
            )
            
            # Set reply-to
            mail.reply_to = Email(self.reply_to_email, "M Supplies")
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            response = sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                logger.info(f"Signup notification sent to {self.admin_email}")
                return True
            else:
                logger.error(f"Failed to send signup notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending signup notification: {str(e)}")
            return False

    async def send_welcome_email(
        self,
        email: str,
        display_name: str
    ) -> bool:
        """Send welcome email to new user"""
        
        if not self.api_key:
            logger.warning("Cannot send email - SendGrid API key not configured")
            return False
        
        try:
            # HTML welcome email for user
            html_body = f"""
<h2 style="font-family:Inter,Arial,sans-serif;color:#333;margin:0 0 12px;">Welcome to M Supplies 🎉</h2>
<p style="font-family:Inter,Arial,sans-serif;color:#444;margin:0 0 16px;">
Thanks for creating your account. To enjoy faster checkout and accurate deliveries, please add your default shipping address.
</p>

<table style="font-family:Inter,Arial,sans-serif;font-size:14px;color:#444;margin:0 0 16px;">
  <tr><td style="padding:2px 0;">👤 Name:</td><td>{display_name}</td></tr>
  <tr><td style="padding:2px 0;">📧 Email:</td><td>{email}</td></tr>
</table>

<p style="margin:0 0 20px;">
  <a href="https://www.msupplies.sg/account?onboard=address" 
     style="background:#111;color:#fff;text-decoration:none;padding:10px 14px;border-radius:6px;display:inline-block;">
    Add My Default Address
  </a>
</p>

<p style="font-family:Inter,Arial,sans-serif;color:#666;font-size:12px;margin:24px 0 0;">
You can update your details anytime under <strong>My Account → Addresses</strong>.
</p>
<hr style="border:none;border-top:1px solid #eee;margin:16px 0;">
<p style="font-family:Inter,Arial,sans-serif;color:#999;font-size:12px;margin:0;">M Supplies (INT) Pte Ltd — Official Store</p>
"""
            
            # Plain text version
            text_body = f"""
Welcome to M Supplies 🎉

Thanks for creating your account, {display_name}!

To enjoy faster checkout and accurate deliveries, please add your default shipping address:
https://www.msupplies.sg/account?onboard=address

You can update your details anytime under My Account → Addresses.

M Supplies (INT) Pte Ltd — Official Store
"""
            
            mail = Mail(
                from_email=Email(self.from_email, "M Supplies"),
                to_emails=To(email),
                subject="Welcome to M Supplies 🎉 Please complete your delivery address",
                plain_text_content=Content("text/plain", text_body),
                html_content=Content("text/html", html_body)
            )
            
            # Set reply-to
            mail.reply_to = Email(self.reply_to_email, "M Supplies")
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            response = sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                logger.info(f"Welcome email sent to {email}")
                return True
            else:
                logger.error(f"Failed to send welcome email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()