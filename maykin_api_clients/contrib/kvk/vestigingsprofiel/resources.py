from maykin_api_clients.core import BaseResource, RetrieveOperation

from ..common import Vestiging
from .parameters import VestigingsprofielArgs


class VestigingsprofielResource(BaseResource):
    retrieve = RetrieveOperation(
        path="v1/vestigingsprofielen/{vestigingsnummer}",
        call_args=VestigingsprofielArgs,
        returns=Vestiging,
    )
