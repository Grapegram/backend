from seedwork.domain.rule import BusinessRule
from src.generic.iam.domain.value_objects.email import Email
from src.generic.iam.domain.value_objects.password import HashedPassword


class NewPasswordMustBeDifferentFromPreviousPassword(BusinessRule):
    __message = "The new password must be different from the previous password."

    prev_password: HashedPassword
    new_password: HashedPassword

    def is_broken(self) -> bool:
        return self.prev_password == self.new_password


class NewEmailMustBeDifferentFromPreviousEmail(BusinessRule):
    __message = "The new email must be different from the previous email."

    prev_email: Email
    new_email: Email

    def is_broken(self) -> bool:
        return self.prev_email == self.new_email
