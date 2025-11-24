from dataclasses import dataclass

from seedwork.domain.rule import BusinessRule

from .value_objects import Email, HashedPassword


@dataclass
class NewPasswordMustBeDifferentFromPreviousPassword(BusinessRule):
    """The new password must be different from the previous password."""

    prev_password: HashedPassword
    new_password: HashedPassword

    def is_broken(self) -> bool:
        return self.prev_password == self.new_password


@dataclass
class NewEmailMustBeDifferentFromPreviousEmail(BusinessRule):
    """The new email must be different from the previous email."""

    prev_email: Email
    new_email: Email

    def is_broken(self) -> bool:
        return self.prev_email == self.new_email
