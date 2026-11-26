from maykin_api_clients.core import RetrieveOperation

from ..common import KvKResource, Vestiging
from .parameters import VestigingsprofielArgs


class VestigingsprofielResource(KvKResource):
    retrieve = RetrieveOperation(
        path="v1/vestigingsprofielen/{vestigingsnummer}",
        call_args=VestigingsprofielArgs,
        returns=Vestiging,
    )
