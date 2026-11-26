from maykin_api_clients.core import RetrieveOperation

from ..common import KvKNummerArgs, KvKResource
from .structs import Naamgeving


class NaamgevingResource(KvKResource):
    retrieve = RetrieveOperation(
        path="v1/naamgevingen/kvknummer/{kvk_nummer}",
        call_args=KvKNummerArgs,
        returns=Naamgeving,
    )
