from collections.abc import Sequence
from datetime import date, datetime
from uuid import UUID

from maykin_api_clients.core import BaseSchemaStruct

from ..typing import ProductTypeAllowedStates


class NestedProductType(BaseSchemaStruct):
    uuid: UUID
    code: str
    naam: str
    uniforme_product_naam: str
    toegestane_statussen: Sequence[ProductTypeAllowedStates] | None = None
    gepubliceerd: bool
    aanmaak_datum: datetime
    update_datum: datetime
    taal: str
    keywords: Sequence[str] | None = None
    publicatie_start_datum: date | None = None
    publicatie_eind_datum: date | None = None


class Theme(BaseSchemaStruct):
    uuid: UUID
    naam: str
    beschrijving: str | None = None
    gepubliceerd: bool | None = None
    aanmaak_datum: datetime
    update_datum: datetime
    hoofd_thema: str | None = None
    producttypen: Sequence[NestedProductType]
