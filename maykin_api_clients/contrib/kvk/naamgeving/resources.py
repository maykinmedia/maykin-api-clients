from maykin_api_clients.core import BaseResource, RetrieveOperation

from ..common import KvKNummerArgs
from .structs import Naamgeving


class NaamgevingResource(BaseResource):
    retrieve = RetrieveOperation(
        path="v1/naamgevingen/kvknummer/{kvk_nummer}",
        call_args=KvKNummerArgs,
        returns=Naamgeving,
    )
