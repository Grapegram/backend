from .change_password import ChangePassword
from .change_user_avatar import ChangeUserAvatar
from .login import Login
from .registration_by_email import RegistrationByEmail
from .verification_email import VerifyEmail

__all__ = [
    "RegistrationByEmail",
    "Login",
    "VerifyEmail",
    "ChangePassword",
    "ChangeUserAvatar",
]
