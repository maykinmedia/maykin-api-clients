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
from collections.abc import Callable, Collection
from typing import Generic, Self, TypeVar, final
from urllib.parse import quote

from typing_extensions import ParamSpec  # to be able to pass a default

from .parameters import NoArgs, QueryArgsProtocol, QueryParams
from .resources import BaseResource

# can't set a bound, because even a detail endoint could return something other than
# a mapping/dict
R = TypeVar("R")
P = ParamSpec("P", default=[])  # default for when P is empty and cannot be inferred


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

    @final
    @staticmethod
    def _check_arguments(
        path: str,
        path_fields: Collection[str],
        args: Callable[..., object],
    ):
        args_name = repr(args)
        parameters = inspect.signature(args).parameters
        if any(
            p
            for p in parameters.values()
            if p.kind is not inspect.Parameter.KEYWORD_ONLY
        ):
            raise TypeError(f"{args_name} must only accept keyword arguments")

        if missing := set(path_fields) - parameters.keys():
            raise TypeError(
                f"path {path!r} expects path parameters {','.join(sorted(missing))}, "
                f"which {'is' if len(missing) == 1 else 'are'} not declared "
                f"in {args_name}"
            )

    @final
    @staticmethod
    def interpolate_path(
        path: str,
        args_holder: object,
        path_params: Collection[str],
    ) -> str:
        return path.format_map(
            {
                name: quote(str(getattr(args_holder, name)), safe="")
                for name in path_params
            }
        )


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
        self.path = path
        self.arguments = call_args
        self.returns = returns

        # extract the path placeholders, e.g. foo/{uuid}/bar -> extracts 'uuid'
        self._path_fields = {
            name for _, name, _, _ in string.Formatter().parse(path) if name
        }
        if __debug__:
            self._check_arguments(path, self._path_fields, call_args)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """
        Execute the retrieve operation.

        The configured path is interpolated with the provided path arguments. If there
        are query parameters provided, they're passed along to the underlying GET call.

        The HTTP response JSON is processed into the specified return type.
        """
        assert not args, "Positional arguments should not be possible/allowed"
        # instantate the arguments - this gives access to the defaults if a parameter
        # is optional and not provided, which raw **kwargs access does not. Raw **kwargs
        # access would be most performant, but inspect.Signature.bind is about 10-15
        # times slower to work around the **kwargs defaults.
        args_holder = self.arguments(*args, **kwargs)

        # enforce consistent naming for the query params argument by only consuming
        # .params here
        params: QueryParams | None = None
        if isinstance(args_holder, QueryArgsProtocol):
            params = args_holder.params

        path = self.interpolate_path(self.path, args_holder, self._path_fields)
        resource = self.resource
        # TODO: support for headers=... -> would be an actual example of defaults to
        # apply!
        response = resource._get(path, params=params)
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
