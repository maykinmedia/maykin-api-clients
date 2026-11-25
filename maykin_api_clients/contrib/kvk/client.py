from typing import NotRequired

from ape_pie import APIClient
from requests.structures import CaseInsensitiveDict
from requests.utils import default_headers
from typing_extensions import TypedDict

from .basisprofiel import BasisprofielResource
from .naamgeving import NaamgevingResource
from .vestigingsprofiel import VestigingsprofielResource
from .zoeken import ZoekenResource

# The KvK APIs are versioned independently (e.g. Basisprofiel is v1, Zoeken is v2),
# so the version is part of each resource's paths rather than the base URL.
KVK_PRODUCTION_URL = "https://api.kvk.nl/api/"
KVK_TEST_URL = "https://api.kvk.nl/test/api/"

# NOTE: both environments use the "Staat der Nederlanden Private Root CA – G1"
# certificate chain, which is not in the certifi bundle. Pass ``verify=...`` via
# ``request_kwargs``.


class RequestKwargs(TypedDict, extra_items=object):
    headers: NotRequired[CaseInsensitiveDict[str]]


class KvKClient(APIClient):
    """
    Client for the KvK APIs.
    """

    Basisprofiel = BasisprofielResource()
    Naamgeving = NaamgevingResource()
    Vestigingsprofiel = VestigingsprofielResource()
    Zoeken = ZoekenResource()

    def __init__(
        self,
        base_url: str = KVK_PRODUCTION_URL,
        *,
        api_key: str,
        request_kwargs: RequestKwargs | None = None,
        **kwargs,
    ):
        request_kwargs = request_kwargs or {}
        self._set_default_headers(request_kwargs=request_kwargs, api_key=api_key)

        # FIXME: fix up type in ape-pie (together with context manager depth tracking)
        super().__init__(
            base_url=base_url,
            request_kwargs=request_kwargs,  # pyright: ignore[reportArgumentType]
            **kwargs,
        )

    def _set_default_headers(  # mutates the request_kwargs (!)
        self,
        *,
        request_kwargs: RequestKwargs,
        api_key: str,
    ) -> None:
        if "headers" not in request_kwargs:
            request_kwargs["headers"] = default_headers()
            request_kwargs["headers"]["User-Agent"] = "KvKClient"

        request_kwargs["headers"]["apikey"] = api_key
