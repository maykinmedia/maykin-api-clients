from __future__ import annotations

import copy
import logging
from collections.abc import Mapping
from typing import Self

import msgspec
import requests
from ape_pie import APIClient

from .query_params import QueryParams

logger = logging.getLogger(__name__)


type Headers = Mapping[str, str]
"""
Case-insensitive mapping of HTTP headers.

Primarily used to model HTTP request headers.
"""


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
        # (no __set__), the instance attribute now shadows it, so later
        # accesses skip __get__ and return the same bound resource.
        client.__dict__[self._name] = bound

        return bound

    def __set__(self, *args, **kwargs):
        raise NotImplementedError("Deliberately not supported.")

    @property
    def http_client(self) -> C:
        if self._http_client is None:
            raise RuntimeError(
                f"{type(self).__name__} is not bound to a client; access it through a "
                "client instance."
            )
        return self._http_client

    @staticmethod
    def process_response[T](
        response: requests.Response,
        struct: type[T],
    ) -> T:
        """
        Perform the necessary processing on the retrieved data.

        The JSON data is processed and converted to msgspec structs. This includes the
        validation of the incoming data.

        .. todo:: Implement proper error handling with response-shape aware structs.
        """
        # for now: assume no errors :)
        # response.raise_for_status()

        response_data = response.json()
        return msgspec.convert(response_data, type=struct)

    def _get(
        self,
        path: str,
        headers: Headers | None = None,
        params: QueryParams | None = None,
    ) -> requests.Response:
        query_params = params.as_params() if params is not None else None
        response = self.http_client.request(
            "get", path, headers=headers, params=query_params
        )
        return response

    # def _post(
    #     self,
    #     path: str,
    #     headers: Headers | None = None,
    #     params: QueryParams | None = None,
    #     data: object = None,
    # ) -> requests.Response:
    #     query_params = params.as_params() if params is not None else None
    #     response = self.http_client.request(
    #         "post",
    #         path,
    #         headers=headers,
    #         json=data,
    #         params=query_params,
    #     )
    #     return response

    # def _put(
    #     self,
    #     path: str,
    #     headers: Headers | None = None,
    #     params: QueryParams | None = None,
    #     data: object = None,
    # ) -> requests.Response:
    #     query_params = params.as_params() if params is not None else None
    #     response = self.http_client.request(
    #         "put", path, headers=headers, json=data, params=query_params
    #     )
    #     return response

    # def _delete(
    #     self,
    #     path: str,
    #     headers: Headers | None = None,
    #     params: QueryParams | None = None,
    # ) -> requests.Response:
    #     query_params = params.as_params() if params is not None else None
    #     response = self.http_client.request(
    #         "delete",
    #         path,
    #         headers=headers,
    #         params=query_params,
    #     )
    #     return response

    # def _patch(
    #     self,
    #     path: str,
    #     headers: Headers | None = None,
    #     params: QueryParams | None = None,
    #     data: object = None,
    # ) -> requests.Response:
    #     query_params = params.as_params() if params is not None else None
    #     response = self.http_client.request(
    #         "patch",
    #         path,
    #         headers=headers,
    #         params=query_params,
    #         json=data,
    #     )
    #     return response

    # def _options(
    #     self,
    #     path: str,
    #     headers: Headers | None = None,
    #     params: QueryParams | None = None,
    # ) -> requests.Response:
    #     query_params = params.as_params() if params is not None else None
    #     response = self.http_client.request(
    #         "options",
    #         path,
    #         headers=headers,
    #         params=query_params,
    #     )
    #     return response
