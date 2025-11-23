from pydantic import BaseModel


class IAMSettings(BaseModel):
    """Settings for IAM module."""

    # JWT Settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    verification_token_expire_minutes: int = 60 * 24  # 24 hours
    password_reset_token_expire_minutes: int = 60  # 1 hour

    # Password Hashing Settings
    password_hash_iterations: int = 600_000
    password_salt: bytes | None = None

    # SMTP Settings
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@grapegram.com"
    smtp_from_name: str = "Grapegram"
    smtp_use_tls: bool = False

    # Email URL Templates
    email_verification_url_template: str = (
        "https://grapegram.com/verify-email?token={token}"
    )
    email_password_reset_url_template: str = (
        "https://grapegram.com/reset-password?token={token}"
    )
    email_dashboard_url: str = "https://grapegram.com/dashboard"
    email_support_email: str = "support@grapegram.com"
