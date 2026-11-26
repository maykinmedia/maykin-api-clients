from collections.abc import Sequence

from maykin_api_clients.core import UNSET, UnsetType

from ..common import Handelsnaam, KvKDate, KvKStruct, Links

# NOTE: the Naamgeving spec (v1.1.1, see specs/kvk/naamgeving.yaml) is incorrect about
# ``links``. Its schemas declare an object with named keys (``self``/``basisprofiel``
# on Naamgeving, ``vestigingsprofiel`` on the vestigingen), but the API returns the
# same array of ``{rel, href, title}`` link objects as the other KvK APIs - which
# matches the ``example`` in the spec itself. We model what the API actually returns.
# Verified against the test environment on 2026-11-25.


class NaamgevingVestiging(KvKStruct):
    """
    A commerciële or niet-commerciële vestiging.

    The spec declares ``oneOf: [CommercieleVestiging, NietCommercieleVestiging]``
    without a discriminator. msgspec can't decode an untagged union of structs, so
    both shapes are merged into a single struct:

    * commercieel: ``eerste_handelsnaam`` and ``handelsnamen``
    * niet-commercieel: ``naam`` and ``ook_genoemd``
    """

    vestigingsnummer: str  # 12 digits
    # deviates from the spec - see the note at the top of the module
    links: Links | UnsetType = UNSET
    # CommercieleVestiging
    eerste_handelsnaam: str | UnsetType = UNSET
    handelsnamen: Sequence[Handelsnaam] | UnsetType = UNSET
    # NietCommercieleVestiging
    naam: str | UnsetType = UNSET
    ook_genoemd: str | UnsetType = UNSET


class Naamgeving(KvKStruct):
    kvk_nummer: str
    rsin: str | UnsetType = UNSET  # 9 digits, may contain leading zeroes
    statutaire_naam: str | UnsetType = UNSET
    naam: str | UnsetType = UNSET  # naam or eerste handelsnaam
    # alternative name for verenigingen, stichtingen and VvE's
    ook_genoemd: str | UnsetType = UNSET
    startdatum: KvKDate | UnsetType = UNSET
    einddatum: KvKDate | UnsetType = UNSET
    vestigingen: Sequence[NaamgevingVestiging] | UnsetType = UNSET
    # deviates from the spec - see the note at the top of the module
    links: Links | UnsetType = UNSET
