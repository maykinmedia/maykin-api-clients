import msgspec
import pytest

from maykin_api_clients.core import BaseSchemaStruct
from maykin_api_clients.core.operations import as_params


def test_derived_structs_do_not_accept_positional_arguments():
    class MyStruct(BaseSchemaStruct):
        foo: str

    # kwarg-approach is ok
    try:
        MyStruct(foo="foo")
    except TypeError:
        pytest.fail("Keyword arguments must be accepted.")

    # positional args-approach is not ok
    with pytest.raises(TypeError):
        MyStruct("foo")  # type: ignore


def test_rename_configuration_is_inherited():
    class MyBaseStruct(BaseSchemaStruct, rename="camel"):
        pass

    class MyStruct(MyBaseStruct):
        snake_case: str

    result = msgspec.convert({"snakeCase": "camelCase"}, type=MyStruct)

    assert result.snake_case == "camelCase"


def test_query_params_serialize_to_plain_dict():
    class MyParams(BaseSchemaStruct):
        snake_case: str
        camel_case: int = msgspec.field(name="camelCase", default=4)
        optional: msgspec.UnsetType = msgspec.UNSET

    query_params = as_params(MyParams(snake_case="untouched", camel_case=4))

    assert query_params == {
        "snake_case": "untouched",
        "camelCase": 4,
    }
