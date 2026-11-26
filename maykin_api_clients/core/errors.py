"""
Declare how error responses of an API are shaped.

Error declarations mirror the keys of the `OpenAPI responses object`_, so they can be
lifted from a spec almost verbatim:

.. code-block:: python

    errors = {
        404: NotFoundBody,
        "4XX": ClientErrorBody | ValidationErrorBody,
        "default": ErrorBody,
    }

The values are the types to decode the response body into - anything ``msgspec``
understands, including unions (note that msgspec only supports unions of multiple
structs when they're tagged).

.. _OpenAPI responses object: https://spec.openapis.org/oas/v3.0.3#responses-object
"""

from collections.abc import Mapping
from typing import Literal

type StatusKey = int | Literal["1XX", "2XX", "3XX", "4XX", "5XX", "default"]

type ErrorMap = Mapping[StatusKey, object]
"""
Mapping of HTTP status (range) to the expected shape of the error response body.

The value is typed as ``object`` because unions (``A | B``) are not ``type`` instances.
Ideally this would be ``TypeForm[object]`` (PEP 747) once type checkers support it.
"""


_STATUS_RANGES: dict[int, StatusKey] = {
    1: "1XX",
    2: "2XX",
    3: "3XX",
    4: "4XX",
    5: "5XX",
}


def resolve_error_type(errors: ErrorMap, status_code: int) -> object | None:
    """
    Look up the declared error body type for a status code.

    The most specific match wins: the exact status code, then the status range
    (e.g. ``"4XX"``), then ``"default"``.
    """
    keys: list[StatusKey] = [status_code]
    if (range_key := _STATUS_RANGES.get(status_code // 100)) is not None:
        keys.append(range_key)
    keys.append("default")

    for key in keys:
        if key in errors:
            return errors[key]
    return None
