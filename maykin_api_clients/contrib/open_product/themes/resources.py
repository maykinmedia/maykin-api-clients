from maykin_api_clients.core import BaseResource, ListOperation, QueryArgs

from ..common import PaginatedResponseBody
from .parameters import ThemeParams
from .structs import Theme


class ThemeResource(BaseResource):
    list = ListOperation(
        path="producttypen/api/v1/themas",
        call_args=QueryArgs[ThemeParams],
        returns=PaginatedResponseBody[Theme],
    )
