# -*- coding: utf-8 -*-
"""
Email sending service - uses Flask-Mail
"""
from flask import current_app
from flask_mail import Message
from app import mail

class EmailService:
    """Email sending service class using Flask-Mail"""
    
    @staticmethod
    def send_verification_code(to_email, verification_code, purpose='email_change', username=None):
        """Send verification code email"""
        try:
            # 清理邮箱地址
            to_email = to_email.strip()
            
            # 根据目的设置邮件标题和内容
            if purpose == 'email_change':
                subject = 'proISDB - Email Verification Code'
                html_content = EmailService._get_verification_email_template(
                    username, verification_code, purpose='verify email'
                )
            elif purpose == 'registration':
                subject = 'proISDB - Welcome! Verify Your Email'
                html_content = EmailService._get_verification_email_template(
                    username, verification_code, purpose='complete registration'
                )
            else:
                subject = 'proISDB - Verification Code'
                html_content = EmailService._get_verification_email_template(
                    username, verification_code, purpose='verify'
                )
            
            # 使用 Flask-Mail 发送
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_content
            )
            
            mail.send(msg)
            return True, '验证码已发送'
        
        except Exception as e:
            current_app.logger.error(f'Send verification code email失败: {str(e)}')
            return False, f'发送失败: {str(e)}'
    
    @staticmethod
    def _get_verification_email_template(username, code, purpose='verify'):
        """Get verification email template"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">proISDB</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 14px; opacity: 0.9;">IS Element Database</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px 0; font-size: 16px; color: #333333;">
                                Hello{' ' + username if username else ''},
                            </p>
                            
                            <p style="margin: 0 0 30px 0; font-size: 14px; color: #666666; line-height: 1.6;">
                                Thank you for using proISDB. To {purpose}, please use the following verification code:
                            </p>
                            
                            <!-- Verification Code Box -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 0 0 30px 0;">
                                <tr>
                                    <td align="center" style="background-color: #f8f9fa; border-radius: 8px; padding: 30px;">
                                        <div style="font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                            {code}
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 20px 0; font-size: 14px; color: #666666; line-height: 1.6;">
                                This code will expire in <strong>15 minutes</strong>. Please do not share this code with anyone.
                            </p>
                            
                            <p style="margin: 0 0 10px 0; font-size: 14px; color: #999999; line-height: 1.6;">
                                If you didn't request this verification code, please ignore this email.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px 0; font-size: 12px; color: #999999;">
                                © 2026 proISDB. All rights reserved.
                            </p>
                            <p style="margin: 0; font-size: 12px; color: #999999;">
                                This is an automated email, please do not reply.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

