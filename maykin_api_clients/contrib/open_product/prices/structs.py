from collections.abc import Mapping, Sequence
from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from maykin_api_clients.core import UNSET, BaseSchemaStruct, UnsetType

type DMNClassType = Literal[
    "String",
    "Integer",
    "Double",
    "Boolean",
    "Date",
    "Long",
]


class PriceOption(BaseSchemaStruct):
    uuid: UUID | UnsetType = UNSET
    bedrag: Decimal
    beschrijving: str


class DMNMapping(BaseSchemaStruct):
    name: str
    path: str
    classType: DMNClassType


class PriceRule(BaseSchemaStruct):
    uuid: UUID | UnsetType = UNSET
    url: str  # uri
    beschrijving: str
    # mapping between the fields in Open Product & DMN variable
    mapping: Mapping[str, Sequence[DMNMapping]] | None = None


class Price(BaseSchemaStruct):
    uuid: UUID
    producttype_uuid: UUID
    # at runtime, either price options or price rules should be returned
    prijsopties: Sequence[PriceOption] | UnsetType = UNSET
    prijsregels: Sequence[PriceRule] | UnsetType = UNSET
    actief_vanaf: date
