from typing import Final, dataclass_transform

import msgspec
from msgspec import Struct, StructMeta

type UnsetType = msgspec.UnsetType
"""
Type for attributes that may be absent/unset.

The type alias is a library implementation detail that serves as anti-corruption layer
and preventing leaky abstractions.
"""

UNSET: Final[UnsetType] = msgspec.UNSET
"""
Constant

The type alias is a library implementation detail that serves as anti-corruption layer
and preventing leaky abstractions.
"""


@dataclass_transform(kw_only_default=True)
class SchemaStructMeta(StructMeta):
    """
    Configure the behaviour of structs used to interface with APIs.

    The metaclass is the only viable approach to enforce ``kw_only=True``, as it is
    not inherited in msgspec struct subclasses. The behaviour is consistent with
    built-in Python dataclasses.
    """

    def __new__(cls, name, bases, namespace, **struct_config):
        struct_config["kw_only"] = True
        return super().__new__(cls, name, bases, namespace, **struct_config)


class BaseSchemaStruct(Struct, metaclass=SchemaStructMeta):
    """
    Base class for any struct definition used in the client.

    The base class must be used to model API resources, response shapes, (query)
    parameters... Essentially anything that lives under the ``components`` key in the
    OpenAPI specification must inherit from this base class.
    """
