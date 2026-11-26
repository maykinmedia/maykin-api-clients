"""
Shared schema components across the KvK APIs.

The KvK APIs (Basisprofiel, Vestigingsprofiel, Zoeken...) share a number of
components, like addresses, links and the error shape. They're defined once here.
"""

from collections.abc import Mapping, Sequence
from typing import ClassVar

from maykin_api_clients.core import (
    UNSET,
    BaseResource,
    BaseSchemaStruct,
    ErrorMap,
    PathArgs,
    QueryParamsStruct,
    UnsetType,
)

type JaNee = str
"""
KvK models boolean indicators as ``"Ja"``/``"Nee"`` strings.

The spec doesn't declare an enum, so we don't enforce a ``Literal`` either.
"""

type KvKDate = str
"""
Dates are formatted as ``yyyymmdd`` (e.g. ``"20120101"``), not ISO-8601.

Note: ``datumAanvang``/``datumEinde`` can contain partial dates with ``00`` for the
unknown parts, so they cannot reliably be parsed into :class:`datetime.date`.
"""


class KvKStruct(BaseSchemaStruct, rename="camel"):
    """
    Base struct for KvK schemas - the API uses camelCase attribute names.

    The ``rename`` struct config is inherited by subclasses.
    """


class KvKQueryParams(QueryParamsStruct, rename="camel"):
    """
    Base for KvK query parameters - camelCase names and JSON-style booleans.
    """

    def as_params(self) -> Mapping[str, object]:
        # requests serializes ``True`` as ``"True"``, while the spec declares a JSON
        # boolean -> send ``true``/``false``.
        # TODO: consider handling this generically in QueryParamsStruct.as_params
        return {
            key: (str(value).lower() if isinstance(value, bool) else value)
            for key, value in super().as_params().items()
        }


class KvKNummerArgs(PathArgs):
    kvk_nummer: str  # 8 digits


class Link(KvKStruct):
    rel: str | UnsetType = UNSET
    href: str | UnsetType = UNSET  # uri
    title: str | UnsetType = UNSET  # only used by Naamgeving


type Links = Sequence[Link]


class GeoData(KvKStruct):
    """
    BAG (Basisregistratie Adressen en Gebouwen) data from the kadaster.

    Only included when ``geoData=true`` is passed.
    """

    addresseerbaar_object_id: str | UnsetType = UNSET
    nummer_aanduiding_id: str | UnsetType = UNSET
    gps_latitude: float | UnsetType = UNSET
    gps_longitude: float | UnsetType = UNSET
    rijksdriehoek_x: float | UnsetType = UNSET
    rijksdriehoek_y: float | UnsetType = UNSET
    rijksdriehoek_z: float | UnsetType = UNSET


class Adres(KvKStruct):
    type: str | UnsetType = UNSET  # correspondentieadres and/or bezoekadres
    ind_afgeschermd: JaNee | UnsetType = UNSET
    volledig_adres: str | UnsetType = UNSET
    straatnaam: str | UnsetType = UNSET
    huisnummer: int | UnsetType = UNSET
    huisletter: str | UnsetType = UNSET
    huisnummer_toevoeging: str | UnsetType = UNSET
    toevoeging_adres: str | UnsetType = UNSET
    postcode: str | UnsetType = UNSET
    postbusnummer: int | UnsetType = UNSET
    plaats: str | UnsetType = UNSET
    straat_huisnummer: str | UnsetType = UNSET
    postcode_woonplaats: str | UnsetType = UNSET
    regio: str | UnsetType = UNSET
    land: str | UnsetType = UNSET
    geo_data: GeoData | UnsetType = UNSET


class Handelsnaam(KvKStruct):
    naam: str | UnsetType = UNSET
    volgorde: int | UnsetType = UNSET


class MaterieleRegistratie(KvKStruct):
    # Note: in Vestigingsprofiel these are the start/end dates of the vestiging, in
    # Basisprofiel of the onderneming.
    datum_aanvang: KvKDate | UnsetType = UNSET
    datum_einde: KvKDate | UnsetType = UNSET


class SBIActiviteit(KvKStruct):
    sbi_code: str | UnsetType = UNSET
    sbi_omschrijving: str | UnsetType = UNSET
    ind_hoofdactiviteit: JaNee | UnsetType = UNSET


class Vestiging(KvKStruct):
    """
    Full vestiging details - shared by Basisprofiel (hoofdvestiging) and
    Vestigingsprofiel.
    """

    vestigingsnummer: str | UnsetType = UNSET  # 12 digits
    kvk_nummer: str | UnsetType = UNSET  # 8 digits
    # not included in the embedded hoofdvestiging of the basisprofiel
    rsin: str | UnsetType = UNSET
    ind_non_mailing: JaNee | UnsetType = UNSET
    formele_registratiedatum: KvKDate | UnsetType = UNSET
    materiele_registratie: MaterieleRegistratie | UnsetType = UNSET
    statutaire_naam: str | UnsetType = UNSET
    eerste_handelsnaam: str | UnsetType = UNSET
    ind_hoofdvestiging: JaNee | UnsetType = UNSET
    ind_commerciele_vestiging: JaNee | UnsetType = UNSET
    voltijd_werkzame_personen: int | UnsetType = UNSET
    totaal_werkzame_personen: int | UnsetType = UNSET
    deeltijd_werkzame_personen: int | UnsetType = UNSET
    # not included in the embedded hoofdvestiging of the basisprofiel
    handelsnamen: Sequence[Handelsnaam] | UnsetType = UNSET
    adressen: Sequence[Adres] | UnsetType = UNSET
    websites: Sequence[str] | UnsetType = UNSET
    sbi_activiteiten: Sequence[SBIActiviteit] | UnsetType = UNSET
    links: Links | UnsetType = UNSET


#
# Errors
#


class Fout(KvKStruct):
    code: str | UnsetType = UNSET
    omschrijving: str | UnsetType = UNSET


class ErrorResponseBody(KvKStruct):
    """
    Error body for 4xx/5xx responses.
    """

    fout: Sequence[Fout] | UnsetType = UNSET


class KvKResource(BaseResource):
    """
    Base resource for all KvK APIs - they share the same error response shape.

    Note that a 401 has an empty body, which results in ``exc.body`` being ``None``.
    """

    errors: ClassVar[ErrorMap] = {"default": ErrorResponseBody}
