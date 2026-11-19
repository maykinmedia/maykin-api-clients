import msgspec
import pytest

from maykin_api_clients.core.structs import BaseSchemaStruct


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
        MyStruct("foo")


def test_rename_configuration_is_inherited():
    class MyBaseStruct(BaseSchemaStruct, rename="camel"):
        pass

    class MyStruct(MyBaseStruct):
        snake_case: str

    result = msgspec.convert({"snakeCase": "camelCase"}, type=MyStruct)

    assert result.snake_case == "camelCase"
