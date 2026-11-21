from datetime import datetime

from maykin_api_clients.core import (
    UNSET,
    UnsetType,
)

from ..common import PaginationParams


class ThemeParams(PaginationParams):
    # these are some of the available query parameters, append when/if needed
    aanmaak_datum: datetime | UnsetType = UNSET
    gepubliceerd: bool | UnsetType = UNSET
    naam: str | UnsetType = UNSET
    producttypen__uuid: str | UnsetType = UNSET
    update_datum: datetime | UnsetType = UNSET
