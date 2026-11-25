from collections.abc import Sequence

import msgspec

from maykin_api_clients.core import UNSET, UnsetType

from ..common import (
    Adres,
    Handelsnaam,
    JaNee,
    KvKDate,
    KvKStruct,
    Links,
    MaterieleRegistratie,
    SBIActiviteit,
    Vestiging,
)


class VestigingBasis(KvKStruct):
    vestigingsnummer: str | UnsetType = UNSET
    kvk_nummer: str | UnsetType = UNSET
    eerste_handelsnaam: str | UnsetType = UNSET
    ind_hoofdvestiging: JaNee | UnsetType = UNSET
    ind_adres_afgeschermd: JaNee | UnsetType = UNSET
    ind_commerciele_vestiging: JaNee | UnsetType = UNSET
    volledig_adres: str | UnsetType = UNSET
    links: Links | UnsetType = UNSET


class VestigingList(KvKStruct):
    kvk_nummer: str | UnsetType = UNSET
    aantal_commerciele_vestigingen: int | UnsetType = UNSET
    aantal_niet_commerciele_vestigingen: int | UnsetType = UNSET
    totaal_aantal_vestigingen: int | UnsetType = UNSET
    vestigingen: Sequence[VestigingBasis] | UnsetType = UNSET
    links: Links | UnsetType = UNSET


class Eigenaar(KvKStruct):
    rsin: str | UnsetType = UNSET
    rechtsvorm: str | UnsetType = UNSET
    uitgebreide_rechtsvorm: str | UnsetType = UNSET
    datum_uitschrijving: KvKDate | UnsetType = UNSET
    adressen: Sequence[Adres] | UnsetType = UNSET
    websites: Sequence[str] | UnsetType = UNSET
    links: Links | UnsetType = UNSET


class EmbeddedContainer(KvKStruct):
    hoofdvestiging: Vestiging | UnsetType = UNSET
    eigenaar: Eigenaar | UnsetType = UNSET


class Basisprofiel(KvKStruct):
    kvk_nummer: str | UnsetType = UNSET
    ind_non_mailing: JaNee | UnsetType = UNSET
    naam: str | UnsetType = UNSET
    formele_registratiedatum: KvKDate | UnsetType = UNSET
    materiele_registratie: MaterieleRegistratie | UnsetType = UNSET
    totaal_werkzame_personen: int | UnsetType = UNSET
    statutaire_naam: str | UnsetType = UNSET
    handelsnamen: Sequence[Handelsnaam] | UnsetType = UNSET
    sbi_activiteiten: Sequence[SBIActiviteit] | UnsetType = UNSET
    links: Links | UnsetType = UNSET
    # HAL-style key - the leading underscore can't be expressed via camel renaming
    # FIXME: core doesn't expose a ``field`` helper, so this leaks msgspec into contrib
    embedded: EmbeddedContainer | UnsetType = msgspec.field(
        default=UNSET, name="_embedded"
    )
