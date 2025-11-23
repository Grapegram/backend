from dataclasses import dataclass

from seedwork.utils.string import camel_to_snake


class HandlableMeta(type):
    @classmethod
    def _create_tag(cls, cls_instance) -> str:
        return f"{cls_instance.__prefix__}__{camel_to_snake(cls_instance.__name__)}"

    def __new__(cls, name, bases, namespace):
        new_cls = type.__new__(cls, name, bases, namespace)
        new_cls.__base_tag__ = cls._create_tag(new_cls)
        tag = namespace.get("__tag__", None)
        if isinstance(tag, str):
            new_cls.__tag__ = tag
        else:
            new_cls.__tag__ = new_cls.__base_tag__
        return new_cls


@dataclass(frozen=True)
class Handlable(metaclass=HandlableMeta):
    __prefix__ = "handlable"
