from datetime import date

from maykin_api_clients.core import UNSET, UnsetType

from ..common import PaginationParams


class PriceParams(PaginationParams):
    # these are some of the available query parameters, append when/if needed
    actief_vanaf: date | UnsetType = UNSET
    actief_vanaf__gte: date | UnsetType = UNSET
    actief_vanaf__lte: date | UnsetType = UNSET
    producttype__uuid: str | UnsetType = UNSET
