from collections.abc import Mapping
from typing import Protocol

import msgspec

from .structs import BaseSchemaStruct


class QueryParams(Protocol):
    def as_params(self) -> Mapping[str, object]: ...


class QueryParamsStruct(BaseSchemaStruct):
    def as_params(self) -> Mapping[str, object]:
        return msgspec.to_builtins(self)
