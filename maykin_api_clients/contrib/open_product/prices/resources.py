from maykin_api_clients.core import BaseResource, ListOperation, QueryArgs

from ..common import PaginatedResponseBody
from .parameters import PriceParams
from .structs import Price


class PriceResource(BaseResource):
    list = ListOperation(
        path="producttypen/api/v1/prijzen",
        call_args=QueryArgs[PriceParams],
        returns=PaginatedResponseBody[Price],
    )
