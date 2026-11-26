from maykin_api_clients.core import UNSET, QueryArgs, UnsetType

from ..common import KvKQueryParams


class BasisprofielParams(KvKQueryParams):
    geo_data: bool | UnsetType = UNSET


class BasisprofielArgs(QueryArgs[BasisprofielParams]):
    kvk_nummer: str  # 8 digits
