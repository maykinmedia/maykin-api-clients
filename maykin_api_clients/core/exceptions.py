import requests


class ClientError(Exception):
    """
    Base exception class for all error raised by maykin-api-clients.
    """

    is_retriable: bool = False
    """
    Mark an exception type as suitable for automatic retries.

    HTTP 503 errors are transient in nature and thus suitable for automatic retries,
    while HTTP 400 errors typically indicate a client error that won't go away with
    blind retries.
    """


class ClientIOError(ClientError):
    """
    IO-related errors encountered while making requests.

    These errors typically cover generic HTTP-transport errors like DNS issues, SSL
    issues or broken streams etc. Usually downstream projects can't do much about these.
    """


class ClientResponseError(ClientError):
    """
    Errors encountered produced by the API server.

    These are semantic errors that should usually be handled by the projects using the
    clients, different from the IO-errors that are HTTP-transport related.

    :ivar response: The raw HTTP response.
    :ivar status_code: The HTTP status code of the response.
    :ivar body: The response body decoded into the type declared for this status code
      (see :mod:`maykin_api_clients.core.errors`), or ``None`` if no type is declared
      or the body doesn't match the declared type (e.g. an empty 401 response).
    """

    def __init__(self, message: str, *, response: requests.Response, body: object):
        super().__init__(message)
        self.response = response
        self.status_code = response.status_code
        self.body = body
