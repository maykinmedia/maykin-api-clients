from collections.abc import Sequence
from typing import Literal

from maykin_api_clients.core import UNSET, UnsetType

from ..common import KvKQueryParams

type ZoekType = Literal["hoofdvestiging", "nevenvestiging", "rechtspersoon"]


class ZoekenParams(KvKQueryParams):
    """
    Search parameters that can be combined freely.

    Searching by postcode is only possible in combination with a huisnummer or
    postbusnummer (and a huisletter only in combination with a huisnummer). These
    combinations are modelled as the subclasses
    :class:`ZoekenPostcodeHuisnummerParams` and :class:`ZoekenPostcodePostbusParams`,
    so invalid combinations can't be expressed.
    """

    kvk_nummer: str | UnsetType = UNSET  # 8 digits
    rsin: str | UnsetType = UNSET  # 9 digits
    vestigingsnummer: str | UnsetType = UNSET  # 12 digits
    naam: str | UnsetType = UNSET
    straatnaam: str | UnsetType = UNSET
    plaats: str | UnsetType = UNSET
    # serialized as a repeated query parameter: ?type=a&type=b
    type: Sequence[ZoekType] | UnsetType = UNSET
    inclusief_inactieve_registraties: bool | UnsetType = UNSET
    pagina: int | UnsetType = UNSET  # 1-1000, default 1
    resultaten_per_pagina: int | UnsetType = UNSET  # 1-100, default 10


class ZoekenPostcodeHuisnummerParams(ZoekenParams):
    """
    Search by address: postcode and huisnummer, optionally with a huisletter.
    """

    postcode: str  # e.g. 3511BT
    huisnummer: int
    huisletter: str | UnsetType = UNSET


class ZoekenPostcodePostbusParams(ZoekenParams):
    """
    Search by postbus address: postcode and postbusnummer.
    """

    postcode: str  # e.g. 3511BT
    postbusnummer: int
