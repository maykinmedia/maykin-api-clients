from collections.abc import Sequence
from typing import Literal

from maykin_api_clients.core import UNSET, UnsetType

from ..common import JaNee, KvKStruct, Links

type AdresType = Literal["bezoekadres", "postadres"]


class BinnenlandsAdres(KvKStruct):
    type: AdresType | UnsetType = UNSET
    straatnaam: str | UnsetType = UNSET
    huisnummer: int | UnsetType = UNSET
    huisletter: str | UnsetType = UNSET
    # only provided for postadres
    postbusnummer: int | UnsetType = UNSET
    postcode: str | UnsetType = UNSET
    plaats: str | UnsetType = UNSET


class BuitenlandsAdres(KvKStruct):
    type: AdresType | UnsetType = UNSET
    straat_huisnummer: str | UnsetType = UNSET
    postcode_woonplaats: str | UnsetType = UNSET
    land: str | UnsetType = UNSET


class ZoekAdres(KvKStruct):
    """
    Either a domestic or a foreign address.

    Note: differs from the Basisprofiel :class:`~..common.Adres` schema.
    """

    binnenlands_adres: BinnenlandsAdres | UnsetType = UNSET
    buitenlands_adres: BuitenlandsAdres | UnsetType = UNSET


class ResultaatItem(KvKStruct):
    kvk_nummer: str | UnsetType = UNSET
    rsin: str | UnsetType = UNSET
    vestigingsnummer: str | UnsetType = UNSET
    naam: str | UnsetType = UNSET
    adres: ZoekAdres | UnsetType = UNSET
    # hoofdvestiging/nevenvestiging/rechtspersoon - not declared as enum in the spec
    type: str | UnsetType = UNSET
    actief: JaNee | UnsetType = UNSET
    vervallen_naam: str | UnsetType = UNSET
    links: Links | UnsetType = UNSET


class Resultaat(KvKStruct):
    """
    Page of search results. The API returns at most 1000 results in total.
    """

    pagina: int | UnsetType = UNSET
    resultaten_per_pagina: int | UnsetType = UNSET
    totaal: int | UnsetType = UNSET
    vorige: str | UnsetType = UNSET  # link to previous page
    volgende: str | UnsetType = UNSET  # link to next page
    resultaten: Sequence[ResultaatItem] | UnsetType = UNSET
    links: Links | UnsetType = UNSET
