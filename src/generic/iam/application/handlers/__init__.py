from .queries import GetUsersList
from .send_verification_email import SendVerificationEmail

handlers = [SendVerificationEmail, GetUsersList]

__all__ = ["handlers"]
