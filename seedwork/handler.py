from dataclasses import dataclass

from seedwork.utils.string import camel_to_snake


@dataclass(frozen=True)
class Handlable:
    __prefix__ = "handlable"

    @classmethod
    def _create_tag(cls) -> str:
        return f"{cls.__prefix__}__{camel_to_snake(cls.__name__)}"

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "__tag__"):
            cls.__tag__ = cls._create_tag()
