from seedwork.exceptions import FormattedError


class DomainException(FormattedError): ...


class VOValidationException(DomainException): ...
