import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class SMTPEmailService:
    """
    SMTP implementation of EmailService for sending emails.

    This service uses aiosmtplib for async email sending via SMTP
    and Jinja2 for email template rendering.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "Grapegram",
        use_tls: bool = True,
        verification_url_template: str = "https://grapegram.com/verify-email?token={token}",
        password_reset_url_template: str = "https://grapegram.com/reset-password?token={token}",
        dashboard_url: str = "https://grapegram.com/dashboard",
        support_email: str = "support@grapegram.com",
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
        self.use_tls = use_tls
        self.verification_url_template = verification_url_template
        self.password_reset_url_template = password_reset_url_template
        self.dashboard_url = dashboard_url
        self.support_email = support_email

        # Setup Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _render_template(self, template_name: str, context: dict) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email

        # Add plain text part if provided
        if text_body:
            text_part = MIMEText(text_body, "plain")
            message.attach(text_part)

        # Add HTML part
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.use_tls,
            )
            logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise

    async def send_verification_email(
        self, email: str, username: str, token: str
    ) -> None:
        verification_url = self.verification_url_template.format(token=token)

        context = {
            "username": username,
            "verification_url": verification_url,
            "year": datetime.now().year,
        }

        subject = "Verify your email address"
        html_body = self._render_template("verification_email.html", context)
        text_body = self._render_template("verification_email.txt", context)

        await self._send_email(
            to_email=email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

    async def send_password_reset_email(
        self, email: str, username: str, token: str
    ) -> None:
        reset_url = self.password_reset_url_template.format(token=token)

        context = {
            "username": username,
            "reset_url": reset_url,
            "year": datetime.now().year,
        }

        subject = "Reset your password"
        html_body = self._render_template("password_reset_email.html", context)
        text_body = self._render_template("password_reset_email.txt", context)

        await self._send_email(
            to_email=email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

    async def send_welcome_email(self, email: str, username: str) -> None:
        context = {
            "username": username,
            "dashboard_url": self.dashboard_url,
            "support_email": self.support_email,
            "year": datetime.now().year,
        }

        subject = "Welcome to Grapegram!"
        html_body = self._render_template("welcome_email.html", context)
        text_body = self._render_template("welcome_email.txt", context)

        await self._send_email(
            to_email=email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )
