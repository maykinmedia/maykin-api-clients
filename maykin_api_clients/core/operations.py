"""
Provide declarative, statically typed API operations boilerplate.

The operations defined here capture the majority of common RESTful operations. For more
advanced/special cases, define the methods directly on the resource instead, rather than
trying to accomodate every possible feature in the operation classes.

The call signature of an operation is captured with a ``ParamSpec`` from the
constructor of an "arguments" struct, so type checkers and LSPs see exactly
the keyword arguments each operation accepts.
"""

import copy
import inspect
import string
from collections.abc import Callable
from typing import Generic, Self, TypeVar, final, get_origin
from urllib.parse import quote

import msgspec
from typing_extensions import ParamSpec

from .errors import ErrorMap
from .parameters import NoArgs, PayloadArgs, QueryArgsProtocol, QueryParams
from .resources import BaseResource

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
    :param errors: Operation-specific error response shapes, see
      :mod:`maykin_api_clients.core.errors`. Takes precedence over the errors declared
      on the resource.
    """

    def __init__(
        self,
        *,
        path: str,
        returns: type[R],
        # effectively this expects a PathArgs subclass, but the Callable generic allows
        # inferring the __init__ kwargs to apply to the __call__ signature.
        call_args: Callable[P, object] = NoArgs,
        errors: ErrorMap | None = None,
    ):
        self.path = OperationPath(path, call_args)
        self.returns = returns
        self.errors = errors

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
        return resource.process_response(
            response, struct=self.returns, errors=self.errors
        )


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
    :param errors: Operation-specific error response shapes, see
      :mod:`maykin_api_clients.core.errors`. Takes precedence over the errors declared
      on the resource.
    """

    def __init__(
        self,
        *,
        path: str,
        returns: type[R],
        call_args: Callable[P, PayloadArgs] = PayloadArgs,
        errors: ErrorMap | None = None,
    ):
        self.path = OperationPath(path, call_args)
        self.returns = returns
        self.errors = errors

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
        return resource.process_response(
            response, struct=self.returns, errors=self.errors
        )


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
