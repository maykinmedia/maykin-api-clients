from __future__ import annotations

import copy
import logging
from typing import Self, final

from ape_pie import APIClient

logger = logging.getLogger(__name__)


class BaseResource[C: APIClient]:
    """
    Base resource class wrapping the HTTP transport and msgspec conversion patterns.

    Every concrete resource should inherit from this class and specify the concrete
    client class that's expected:

    .. code-block::

        class MyResource(BaseResource[ExpectedClient]):
            def retrieve(self, ...) -> ...:
                ...
    """

    _name: str = ""
    _http_client: C | None = None

    def __set_name__(self, owner: type[C], name: str) -> None:
        self._name = name

    def __get__(self, client: C | None, owner: type[C]) -> Self:
        # class attribute access
        if client is None:
            return self

        # bind the client
        bound = copy.copy(self)
        bound._http_client = client
        # Cache on the instance. Because this is a non-data descriptor
        # (disabled __set__), the instance attribute now shadows it, so later
        # accesses skip __get__ and return the same bound resource.
        client.__dict__[self._name] = bound

        return bound

    def __set__(self, *args, **kwargs):
        raise NotImplementedError("Deliberately not supported.")

    @final
    @property
    def http_client(self) -> C:
        if self._http_client is None:
            raise RuntimeError(
                f"{type(self).__name__} is not bound to a client; access it through a "
                "client instance."
            )
        return self._http_client
