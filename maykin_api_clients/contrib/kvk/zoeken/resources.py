from maykin_api_clients.core import BaseResource, ListOperation, QueryArgs

from .parameters import ZoekenParams
from .structs import Resultaat


class ZoekenResource(BaseResource):
    # NOTE: the API responds with 404 (not an empty result) when nothing matches
    list = ListOperation(
        path="v2/zoeken",
        call_args=QueryArgs[ZoekenParams],
        returns=Resultaat,
    )
