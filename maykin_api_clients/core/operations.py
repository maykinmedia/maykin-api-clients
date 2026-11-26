"""
Provide declarative, statically typed API operations boilerplate.

The operations defined here capture the majority of common RESTful operations. For more
advanced/special cases, define the methods directly on the resource instead, rather than
trying to accomodate every possible feature in the operation classes.

The call signature of an operation is captured with a ``ParamSpec`` from the
constructor of an "arguments" struct, so type checkers and LSPs see exactly
the keyword arguments each operation accepts.
"""

from __future__ import annotations

import copy
import inspect
import string
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, is_dataclass
from typing import (
    TYPE_CHECKING,
    Generic,
    Self,
    TypeVar,
    final,
    get_origin,
    overload,
)
from urllib.parse import quote

import msgspec
from ape_pie.decorators import EndpointMethod
from requests import Response
from typing_extensions import ParamSpec

from .parameters import NoArgs, PayloadArgs, QueryArgsProtocol, QueryParams
from .resources import BaseResource

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

# can't set a bound, because even a detail endoint could return something other than
# a mapping/dict
R = TypeVar("R")
P = ParamSpec("P", default=[])  # default for when P is empty and cannot be inferred


#
# (Path) argument handling
#

T = TypeVar("T")


class OperationPath(Generic[T, P]):
    __slots__ = ("get_args_holder", "path", "path_params")

    def __init__(self, path: str, arg_spec: Callable[P, T]):
        self.path = path
        self.path_params = frozenset(
            {name for _, name, _, _ in string.Formatter().parse(path) if name}
        )
        self.get_args_holder = arg_spec

        if __debug__:
            self.check()

    def __repr__(self):
        return f"<{self.__class__.__name__} path={self.path!r}>"

    def check(self) -> None:
        """
        Check that the arg spec types the provided path template.
        """
        # get_origin is required for when passing call_args=QueryArgs[ParamsType]
        get_args_holder = get_origin(self.get_args_holder) or self.get_args_holder
        args_name = repr(get_args_holder)
        parameters = inspect.signature(get_args_holder).parameters
        parameter_names = set(parameters.keys())

        # check if there are any positional arguments allowed
        if any(
            p
            for p in parameters.values()
            if p.kind is not inspect.Parameter.KEYWORD_ONLY
        ):
            raise TypeError(f"{args_name} must only accept keyword arguments")

        # test if there are any path parameters not specified in the arg spec
        if missing := self.path_params - parameter_names:
            raise TypeError(
                f"path {self.path!r} expects path parameter(s) "
                f"{','.join(sorted(missing))}, which is/are not declared in {args_name}"
            )

        # test if there are any parameters declared in the arg spec *not* in the
        # reserved names or path parameters
        if extra := parameter_names - (self.path_params | {"params", "payload"}):
            raise TypeError(
                f"path {self.path!r} does not expect the path parameter(s) "
                f"{','.join(sorted(extra))}, which is/are declared in {args_name}"
            )

    def evaluate(self, *args: P.args, **kwargs: P.kwargs) -> tuple[str, T]:
        """
        Evaluate the path for the given keyword arguments.

        :returns: a tuple of the the resulting API path and the arguments holder
          holding the non-path arguments.
        """
        assert not args, "Positional arguments should not be possible/allowed"
        # instantate the arguments - this gives access to the defaults if a parameter
        # is optional and not provided, which raw **kwargs access does not. Raw **kwargs
        # access would be most performant, but inspect.Signature.bind is about 10-15
        # times slower to work around the **kwargs defaults.
        args_holder = self.get_args_holder(*args, **kwargs)
        path = self.path.format_map(
            {
                name: quote(str(getattr(args_holder, name)), safe="")
                for name in self.path_params
            }
        )
        return path, args_holder


#
# (Generic) operations
#


class Operation:
    """
    Base API resource operation implementation, providing the common behaviour.

    An operation is an HTTP call of a particular method provided on a particular
    resource endpoint.
    """

    _name: str = ""
    _resource: BaseResource | None = None

    def __set_name__(self, owner: type[BaseResource], name: str) -> None:
        self._name = name

    def __get__(self, resource: BaseResource | None, owner: type[BaseResource]) -> Self:
        # class attribute access
        if resource is None:
            return self

        # bind the resource
        bound = copy.copy(self)
        bound._resource = resource
        # Cache on the instance. Because this is a non-data descriptor
        # (disabled __set__), the instance attribute now shadows it, so later
        # accesses skip __get__ and return the same bound resource.
        resource.__dict__[self._name] = bound

        return bound

    def __set__(self, *args, **kwargs):
        raise NotImplementedError("Deliberately not supported.")

    @final
    @property
    def resource(self) -> BaseResource:
        if self._resource is None:
            raise RuntimeError(
                f"{type(self).__name__} is not bound to a resources; access it through "
                "a bound resource from the client."
            )
        return self._resource


class ReadOperation(Operation, Generic[R, P]):
    """
    Define a read (``GET``) operation.

    The operation must at least define the relative API path to call and the
    expected return struct. When the path contains path arguments, e.g.
    ``my-resource/{id}``, a ``call_args`` type/class must be provided that specifies
    the expected types of these arguments.

    :param path: The path (relative to the API root) to make the GET call to. The
      path can contain path argument placeholders, e.g.
      ``rel-path/{arg1}/fixed/{arg2}`` that will be evaluated at call time.
    :param returns: The expected return value after decoding the response data.
      Should be something that ``msgspec`` understands. If responses are paginated,
      use a struct that models that appropriately.
    :param call_args: A callable - usually a msgspec struct but can be any class or
      function that returns a container for the call arguments. It's signature is
      used for the :meth:`__call__` signature. It's recommended to inherit from
      :class:`maykin_api_clients.core.PathArgs`.
    """

    def __init__(
        self,
        *,
        path: str,
        returns: type[R],
        # effectively this expects a PathArgs subclass, but the Callable generic allows
        # inferring the __init__ kwargs to apply to the __call__ signature.
        call_args: Callable[P, object] = NoArgs,
    ):
        self.path = OperationPath(path, call_args)
        self.returns = returns

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """
        Execute the read operation.

        The configured path is interpolated with the provided path arguments. If there
        are query parameters provided, they're passed along to the underlying GET call.

        The HTTP response JSON is processed into the specified return type.
        """
        path, args_holder = self.path.evaluate(*args, **kwargs)
        # enforce consistent naming for the query params argument by only consuming
        # .params here
        params: QueryParams | None = None
        if isinstance(args_holder, QueryArgsProtocol):
            params = args_holder.params

        # TODO: support for headers=... -> would be an actual example of defaults to
        # apply in the call_args!

        resource = self.resource
        response = resource._get(path, params=params)
        return resource.process_response(response, struct=self.returns)


class CreateOperation(Operation, Generic[R, P]):
    """
    Define a create (``POST``) operation.

    The operation must at least define the relative API path to call, the expected
    return struct and the expected shape of the payload. When the path contains path
    arguments, e.g. ``my-resource/{id}``, the ``call_args`` type/class must declare
    the expected types of these arguments.

    :param path: The path (relative to the API root) to make the GET call to. The
      path can contain path argument placeholders, e.g.
      ``rel-path/{arg1}/fixed/{arg2}`` that will be evaluated at call time.
    :param returns: The expected return value after decoding the response data.
      Should be something that ``msgspec`` understands. If responses are paginated,
      use a struct that models that appropriately.
    :param call_args: A callable - usually a msgspec struct but can be any class or
      function that returns a container for the call arguments. It's signature is
      used for the :meth:`__call__` signature. It's recommended to inherit from
      :class:`maykin_api_clients.core.PayloadArgs`.
    """

    def __init__(
        self,
        *,
        path: str,
        returns: type[R],
        call_args: Callable[P, PayloadArgs] = PayloadArgs,
    ):
        self.path = OperationPath(path, call_args)
        self.returns = returns

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """
        Execute the create operation.

        The configured path is interpolated with the provided path arguments. The
        payload is passed along as JSON to the underlying POST call.

        The HTTP response JSON is processed into the specified return type.
        """
        path, args_holder = self.path.evaluate(*args, **kwargs)

        # TODO: support for headers=... -> would be an actual example of defaults to
        # apply in the call_args!

        resource = self.resource
        response = resource._post(path, json=msgspec.to_builtins(args_holder.payload))
        return resource.process_response(response, struct=self.returns)


ListOperation = ReadOperation
"""
The list operation.

An alias for the read operation, since the list and retrieve operations definitions
effectively must support the same semantics.
"""


RetrieveOperation = ReadOperation
"""
The retrieve operation.

An alias for the read operation, since the list and retrieve operations definitions
effectively must support the same semantics.
"""


def process_response[T](response: Response, into: type[T]) -> T:
    """
    Process the :class:`requests.Response` into structured data.

    .. todo:: Implement default error handling here & discern between IO and semantic
      errors.
    """
    # TODO - error handling. Inspect status code & compose with error handler callback,
    # since different APIs will have different error response shapes.
    # TODO: - error handling: best-effort parse into documented shapes, but fall back
    # to malformed handlers in case an intermediate proxy returns the same error code
    # but with a different content type (e.g. 503 with HTML instead of JSON).

    # for now: assume no errors :)
    # response.raise_for_status()

    response_data = response.json()
    return msgspec.convert(response_data, type=into)


type HttpCallFunc[T, **P] = Callable[P, tuple[Response, type[T]]]
"""
A funtion or method that returns an HTTP response and the struct to decode it into.
"""


class _Operation[T, **P]:
    """
    An operation bound to a resource.

    Calling it makes the HTTP call and processes the response into ``T``.
    """

    def __init__(self, f: HttpCallFunc[T, P]) -> None:
        self.f = f

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        response, output_shape = self.f(*args, **kwargs)
        return process_response(response, into=output_shape)

    def returning[R](self, returns: type[R]) -> _Operation[R, P]:
        """
        Derive the same operation, but processing the response into ``returns``.

        .. code-block:: python

            todo = client.ToDo.retrieve.returning(CustomToDo)(uuid=...)
        """
        f = self.f

        def call_with_override(
            *args: P.args, **kwargs: P.kwargs
        ) -> tuple[Response, type[R]]:
            response, _ = f(*args, **kwargs)
            return response, returns

        return _Operation(call_with_override)


class _OperationMethod[S, **P, T]:
    """
    Descriptor binding an :func:`operation` to the resource it's accessed through.
    """

    def __init__(self, e: EndpointMethod[S, P, tuple[Response, type[T]]]) -> None:
        self.e = e
        self.__doc__ = e.__doc__
        self.__wrapped__ = e

    @overload
    def __get__(self, instance: None, owner: type[object] | None = None) -> Self: ...

    @overload
    def __get__(
        self, instance: S, owner: type[object] | None = None
    ) -> _Operation[T, P]: ...

    def __get__(
        self, instance: S | None, owner: type[object] | None = None
    ) -> Self | _Operation[T, P]:
        # class attribute access
        if instance is None:
            return self
        return _Operation(self.e.__get__(instance, owner))


def operation[S, **P, T](
    e: EndpointMethod[S, P, tuple[Response, type[T]]],
) -> _OperationMethod[S, P, T]:
    """
    Mark an ``@endpoint`` resource method as a JSON API operation.

    The method returns the HTTP response and the struct to decode it into. Calling
    the operation processes the response into that struct. Use
    ``.returning(OtherStruct)`` to process it into another struct for a single call.

    .. code-block:: python

        class TodoResource(BaseResource["APIClient"]):
            @operation
            @endpoint("todos/{uuid}")
            def retrieve(self, url_path: str, /, uuid: UUID):
                return self.http_client.get(url_path), ToDo

    .. todo:: accept arguments, e.g. to override the (default) process_response
      callable. This must support composition.
    """
    return _OperationMethod(e)


type ParamValuePrimitive = str | int | float
type ParamValue = ParamValuePrimitive | Iterable[ParamValuePrimitive]


def as_params(
    params: msgspec.Struct | DataclassInstance | Mapping[str, ParamValue] | None,
) -> Mapping[str, ParamValue] | None:
    """
    Prepare the query params to pass them to :mod:`requests` ``params`` argument.

    .. note:: the type annotations serve as a POC that msgspec isn't a hard dependency.
       In practice, plain dicts & dataclasses are already supported by msgspec too.

    .. todo:: we can't guarantee the runtime value matches the return type (which is a
       narrower type than what requests' ParamsType allows).
    """
    match params:
        case None:
            return None
        case msgspec.Struct():
            return msgspec.to_builtins(params)
        case Mapping():
            return params
        # POC - this could also just go through msgspec.to_builtins()
        case _ if is_dataclass(type(params)):
            return asdict(params)
        case _:
            raise NotImplementedError("Unsupported params type provided.")


# from requests._typing.JsonType
type JsonType = (
    None | bool | int | float | str | Sequence[JsonType] | Mapping[str, JsonType]
)


def as_json(payload: msgspec.Struct | DataclassInstance) -> JsonType:
    return msgspec.to_builtins(payload)
