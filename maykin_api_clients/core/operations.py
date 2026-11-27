"""
Provide declarative, statically typed API operations boilerplate.

.. todo:: update docs :)
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, is_dataclass
from functools import WRAPPER_ASSIGNMENTS, update_wrapper, wraps
from typing import (
    TYPE_CHECKING,
    Concatenate,
    Self,
    overload,
)

import msgspec
from ape_pie.decorators import EndpointMethod, _URLPath, endpoint
from requests import Response

from .resources import BaseResource

if TYPE_CHECKING:
    from _typeshed import DataclassInstance


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
        update_wrapper(self, f, updated=())
        # Resolved eagerly: following __wrapped__ to a bound endpoint method reaches the
        # unbound endpoint's __signature__, which still includes ``self``.
        self.__signature__ = inspect.signature(f)

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

        @wraps(self, updated=())
        def call_with_override(
            *args: P.args, **kwargs: P.kwargs
        ) -> tuple[Response, type[R]]:
            response, _ = f(*args, **kwargs)
            return response, returns

        return _Operation(call_with_override)


class _OperationMethod[S: BaseResource, **P, T]:
    """
    Descriptor binding an :func:`operation` to the resource it's accessed through.
    """

    _name: str = ""

    def __init__(self, e: EndpointMethod[S, P, tuple[Response, type[T]]]) -> None:
        self.e = e
        # Like functools.update_wrapper, which is typed for callables only. Skips
        # copying __dict__, which holds the endpoint's internals.
        for attr in WRAPPER_ASSIGNMENTS:
            try:
                setattr(self, attr, getattr(e, attr))
            except AttributeError:
                pass
        self.__wrapped__ = e

    def __set_name__(self, owner: type[S], name: str) -> None:
        self._name = name

    @overload
    def __get__(self, resource: None, owner: type[object] | None = None) -> Self: ...

    @overload
    def __get__(
        self, resource: S, owner: type[object] | None = None
    ) -> _Operation[T, P]: ...

    def __get__(
        self, resource: S | None, owner: type[object] | None = None
    ) -> Self | _Operation[T, P]:

        # class attribute access
        if resource is None:
            return self

        operation = _Operation(self.e.__get__(resource, owner))
        # Cache on the resource. Because this is a non-data descriptor
        # (disabled __set__), the resource attribute now shadows it, so later
        # accesses skip __get__ and return the same bound resource.
        resource.__dict__[self._name] = operation
        return operation

    def __set__(self, *args, **kwargs):
        raise NotImplementedError("Deliberately not supported.")


class operation:
    """
    Mark a resource method as a JSON API operation on the endpoint ``path``.

    The path is formatted from the method's arguments, like
    :class:`ape_pie.decorators.endpoint`, and passed as the first argument after
    ``self``. The method returns the HTTP response and the struct to decode it into.
    Calling the operation processes the response into that struct. Use
    ``.returning(OtherStruct)`` to process it into another struct for a single call.

    .. code-block:: python

        class TodoResource(BaseResource["APIClient"]):
            @operation("todos/{uuid}")
            def retrieve(self, url_path: str, /, uuid: UUID):
                return self.http_client.get(url_path), ToDo

    .. todo:: accept arguments, e.g. to override the (default) process_response
      callable. This must support composition.
    """

    def __init__(self, path: str) -> None:
        self._endpoint = endpoint(path)

    def __call__[S: BaseResource, **P, T](
        self,
        f: Callable[Concatenate[S, _URLPath, P], tuple[Response, type[T]]],
        /,
    ) -> _OperationMethod[S, P, T]:
        if __debug__:
            _check_signature(f)
        return _OperationMethod(self._endpoint(f))


def _check_signature(method: Callable[..., object]) -> None:
    """
    Introspect the method signature and enforce conventions.

    Conventions established with the team:

    * keywords only, the only exception is the generated 'url_path' positional argument
      from :class:`ape_pie.decorators.endpoint` that's automatically injected and must
      be positional due to limitations in the typing system.
    * use the ``_url_path`` name with the underscore to signal there's something
      "special" about it. This is primarily aimed at developers looking at the source
      code to see what the expected arguments are, rather than relying on their IDE/LSP
      integration.
    * Given the context of our client with resource classes, we expect methods that take
      a 'self' argument, which they usually need to make the underlying HTTP call.
    """
    # enforce conventions
    sig = inspect.signature(method)
    params = list(sig.parameters.values())
    dotted_path = f"{method.__module__}.{method.__qualname__}"
    if len(params) <= 2:  # param 1 is self, param 2 must be the url path
        raise TypeError(f"{dotted_path} must take the '_url_path' positional argument.")

    assert params[0].name == "self"
    if params[1].name != "_url_path":
        raise TypeError(
            f"{dotted_path} must use the name '_url_path' for the formatted "
            "endpoint path (convention enforcement)."
        )

    rest = params[2:]
    if any(
        p.kind not in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD)
        for p in rest
    ):
        raise TypeError(
            f"{dotted_path}'s additional arguments must be keyword only. Hint: "
            "use 'def operation(self, _url_path, *, kwarg1, kwarg2): ...'"
        )


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
