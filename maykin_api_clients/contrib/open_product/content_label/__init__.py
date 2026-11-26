from maykin_api_clients.core import (
    BaseResource,
    BaseSchemaStruct,
    ListOperation,
    QueryArgs,
)

from ..common import PaginatedResponseBody, PaginationParams

__all__ = ["ContentLabel", "ContentLabelResource"]


class ContentLabel(BaseSchemaStruct):
    naam: str


class ContentLabelResource(BaseResource):
    list = ListOperation(
        path="producttypen/api/v1/contentlabels",
        call_args=QueryArgs[PaginationParams],
        returns=PaginatedResponseBody[ContentLabel],
    )
