"""
Define (base) types to work with operation parameters.

The parameters term is borrowed from `OpenAPI parameters`_. In this module, we cover:

* path parameters: variable segments in URL paths
* query parameters: parameters that go in the query string for an HTTP call
* (request) headers

The full set of parameters are combined into the :class:`Args` concept, and is crucial
to make strongly typed call signatures of operations possible.

.. _OpenAPI parameters: https://swagger.io/docs/specification/v3_0/describing-parameters/
"""

from collections.abc import Collection, Mapping
from typing import Protocol, final, runtime_checkable

import msgspec

from .structs import BaseSchemaStruct

#
# HTTP (request) headers
#

type Headers = Mapping[str, str]
"""
Case-insensitive mapping of HTTP headers.

Primarily used to model HTTP request headers.
"""

#
# Query parameters
#


class QueryParams(Protocol):
    def as_params(self) -> Mapping[str, object]:
        """
        Serialize the object to something understood by requests ``headers`` argument.
        """
        ...


class QueryParamsStruct(BaseSchemaStruct):
    """
    Base implementation for msgspec-backed query parameter definitions.

    .. todo:: do we want to keep this (initially)? Calling msgspec.to_builtins() on the
       params already supports plain dicts/lists, dataclasses and structs...
    """

    def as_params(self) -> Mapping[str, object]:
        return msgspec.to_builtins(self)


#
# Path Parameters
#


class PathArgs(BaseSchemaStruct):
    """
    Base implementation for msgspec-backed path parameter definitions.

    Any declarated attribute in subclasses is expected to map to a URL path parameter.

    .. warning:: the attribute name ``params`` is reserved for query parameters.
    .. warning:: the attribute name ``payload`` is reserved for write payloads.
    """


#
# Combining different kinds of parameters
#


@runtime_checkable
class QueryArgsProtocol[Q: QueryParams](Protocol):
    params: Q | None = None


@final
class NoArgs(BaseSchemaStruct):
    """
    Default to signal no path/query params are expected.
    """


class QueryArgs[Q: QueryParams](PathArgs):
    """
    Base implementation for call arguments with support for query parameters.

    The name ``params`` is reserved for the query params type. Any other declarated
    attribute in subclasses is expected to map to a URL path parameter.
    """

    params: Q | None = None


class PayloadArgs[P: BaseSchemaStruct | Collection[BaseSchemaStruct]](PathArgs):
    """
    Base implementation for call arguments that take a payload.

    Write operations like create, update, partial update require a payload to be sent.
    The name ``payload`` is reserved for the payload type. Any other declarated
    attribute in subclasses is expected to map to a URL path parameter (unless
    potentially combined with query arguments).

    The payload is expected to be some kind of struct-like type understood by
    msgspec. It may also be a container (in practice: list/array), as long as it can
    be serialied to JSON.
    """

    payload: P
