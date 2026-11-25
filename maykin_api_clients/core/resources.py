from __future__ import annotations

import copy
import logging
from typing import ClassVar, Self, final

import msgspec
import requests
from ape_pie import APIClient

from .errors import ErrorMap, StatusKey, resolve_error_type
from .exceptions import ClientIOError, ClientResponseError
from .parameters import Headers, QueryParams

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

    errors: ClassVar[ErrorMap] = {}
    """
    Error response shapes shared by all operations of the resource.

    Operations can declare their own ``errors``, which take precedence. Define a base
    resource class for an API to share the error declarations across resources.
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

    def process_response[T](
        self,
        response: requests.Response,
        struct: type[T],
        errors: ErrorMap | None = None,
    ) -> T:
        """
        Perform the necessary processing on the retrieved data.

        The JSON data is processed and converted to msgspec structs. This includes the
        validation of the incoming data.

        :param errors: Operation-specific error declarations, taking precedence over
          the resource-level :attr:`errors`.
        :raises ClientResponseError: if the response has a 4xx or 5xx status code.
        """
        if not response.ok:
            # operation-level declarations take precedence
            all_errors: dict[StatusKey, object] = dict(self.errors)
            if errors:
                all_errors.update(errors)
            raise self.build_response_error(response, errors=all_errors)

        response_data = response.json()
        return msgspec.convert(response_data, type=struct)

    def build_response_error(
        self, response: requests.Response, errors: ErrorMap
    ) -> ClientResponseError:
        """
        Build the exception for an error response, decoding the body if possible.

        Decoding failures of the error body are not raised - the error response itself
        is the more relevant information. Override this for API-specific exception
        classes.
        """
        body: object = None
        if (error_type := resolve_error_type(errors, response.status_code)) is not None:
            try:
                body = msgspec.json.decode(response.content, type=error_type)
            except msgspec.DecodeError:  # also covers ValidationError
                logger.warning(
                    "Error response body of %s %s does not match the declared type %r",
                    response.request.method if response.request else "?",
                    response.url,
                    error_type,
                    exc_info=True,
                )

        return ClientResponseError(
            f"{response.status_code} {response.reason} for url: {response.url}",
            response=response,
            body=body,
        )

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        try:
            return self.http_client.request(method, path, **kwargs)
        except requests.RequestException as exc:
            raise ClientIOError(str(exc)) from exc

    def _get(
        self,
        path: str,
        headers: Headers | None = None,
        params: QueryParams | None = None,
    ) -> requests.Response:
        query_params = params.as_params() if params is not None else None
        response = self._request("get", path, headers=headers, params=query_params)
        return response

    def _post(
        self,
        path: str,
        headers: Headers | None = None,
        params: QueryParams | None = None,
        json: object = None,  # typed as Any in requests
    ) -> requests.Response:
        query_params = params.as_params() if params is not None else None
        response = self._request(
            "post",
            path,
            headers=headers,
            json=json,
            params=query_params,
        )
        return response

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
