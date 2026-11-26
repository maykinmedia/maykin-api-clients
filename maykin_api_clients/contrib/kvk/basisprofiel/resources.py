from maykin_api_clients.core import RetrieveOperation

from ..common import KvKNummerArgs, KvKResource
from .parameters import BasisprofielArgs
from .structs import Basisprofiel, Eigenaar, Vestiging, VestigingList


class BasisprofielResource(KvKResource):
    retrieve = RetrieveOperation(
        path="v1/basisprofielen/{kvk_nummer}",
        call_args=BasisprofielArgs,
        returns=Basisprofiel,
    )
    eigenaar = RetrieveOperation(
        path="v1/basisprofielen/{kvk_nummer}/eigenaar",
        call_args=BasisprofielArgs,
        returns=Eigenaar,
    )
    hoofdvestiging = RetrieveOperation(
        path="v1/basisprofielen/{kvk_nummer}/hoofdvestiging",
        call_args=BasisprofielArgs,
        returns=Vestiging,
    )
    # the only endpoint without geoData query parameter
    vestigingen = RetrieveOperation(
        path="v1/basisprofielen/{kvk_nummer}/vestigingen",
        call_args=KvKNummerArgs,
        returns=VestigingList,
    )
