class ClientError(Exception):
    """
    Base exception class for all error raised by maykin-api-clients.
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
    """
