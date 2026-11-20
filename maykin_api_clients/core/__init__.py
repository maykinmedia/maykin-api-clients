"""
Core building blocks that all clients, resources, structs... should build upon.

Keep API-specific code out of this package - instead create a subpackage in
:mod:`maykin_api_clients.contrib`.
"""

from .exceptions import ClientError, ClientIOError, ClientResponseError
from .operations import ListOperation, RetrieveOperation
from .parameters import PathArgs, QueryArgs, QueryParamsStruct
from .resources import BaseResource
from .structs import UNSET, BaseSchemaStruct, UnsetType

__all__ = [
    "UNSET",
    "BaseResource",
    "BaseSchemaStruct",
    "ClientError",
    "ClientIOError",
    "ClientResponseError",
    "ListOperation",
    "PathArgs",
    "QueryArgs",
    "QueryParamsStruct",
    "RetrieveOperation",
    "UnsetType",
]
