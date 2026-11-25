"""
Core building blocks that all clients, resources, structs... should build upon.

Keep API-specific code out of this package - instead create a subpackage in
:mod:`maykin_api_clients.contrib`.
"""

from .errors import ErrorMap
from .exceptions import ClientError, ClientIOError, ClientResponseError
from .operations import CreateOperation, ListOperation, RetrieveOperation
from .parameters import PathArgs, PayloadArgs, QueryArgs, QueryParamsStruct
from .resources import BaseResource
from .structs import UNSET, BaseSchemaStruct, UnsetType

__all__ = [
    "UNSET",
    "BaseResource",
    "BaseSchemaStruct",
    "ClientError",
    "ClientIOError",
    "ClientResponseError",
    "CreateOperation",
    "ErrorMap",
    "ListOperation",
    "PathArgs",
    "PayloadArgs",
    "QueryArgs",
    "QueryParamsStruct",
    "RetrieveOperation",
    "UnsetType",
]
