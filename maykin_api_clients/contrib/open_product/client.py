from typing import Literal, NotRequired

from ape_pie import APIClient
from requests.structures import CaseInsensitiveDict
from requests.utils import default_headers
from typing_extensions import TypedDict

from .themes import ThemeResource


class RequestKwargs(TypedDict, extra_items=object):
    headers: NotRequired[CaseInsensitiveDict[str]]


class OpenProductClient(APIClient):
    Theme = ThemeResource()

    def __init__(
        self,
        base_url: str,
        *,
        token: str = "",
        language_code: Literal["nl", "en"] = "nl",
        request_kwargs: RequestKwargs | None = None,
        **kwargs,
    ):
        request_kwargs = request_kwargs or {}
        self._set_default_headers(
            request_kwargs=request_kwargs, language_code=language_code, token=token
        )

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
        language_code: str,
        token: str,
    ) -> None:
        if "headers" not in request_kwargs:
            request_kwargs["headers"] = default_headers()
            request_kwargs["headers"]["User-Agent"] = "OpenProductClient"

        request_kwargs["headers"]["Accept-Language"] = language_code
        if token:
            request_kwargs["headers"]["Authorization"] = f"Token {token}"
