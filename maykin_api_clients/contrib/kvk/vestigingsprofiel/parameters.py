from maykin_api_clients.core import UNSET, QueryArgs, UnsetType

from ..common import KvKQueryParams


class VestigingsprofielParams(KvKQueryParams):
    geo_data: bool | UnsetType = UNSET


class VestigingsprofielArgs(QueryArgs[VestigingsprofielParams]):
    vestigingsnummer: str  # 12 digits
