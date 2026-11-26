from collections.abc import Sequence

from maykin_api_clients.core import (
    UNSET,
    BaseSchemaStruct,
    QueryParamsStruct,
    UnsetType,
)


class PaginationParams(QueryParamsStruct):
    page: int | UnsetType = UNSET
    page_size: int | UnsetType = UNSET


class PaginatedResponseBody[T: BaseSchemaStruct](BaseSchemaStruct):
    count: int
    next: str | None
    previous: str | None
    results: Sequence[T]
