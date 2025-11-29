from src.core.chat.infrastructure.models import models as chat_models
from src.generic.iam.infrastructure.models import models as iam_models

models = [*iam_models, *chat_models]
__all__ = ["models"]
