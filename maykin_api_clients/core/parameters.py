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

from collections.abc import Mapping

type Headers = Mapping[str, str]
"""
Case-insensitive mapping of HTTP headers.

Primarily used to model HTTP request headers.
"""
