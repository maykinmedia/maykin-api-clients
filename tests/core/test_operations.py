import pytest

from maykin_api_clients.core import BaseSchemaStruct, PathArgs, RetrieveOperation


def test_retrieve_operation_instantiates_for_paths_without_arguments():
    operation = RetrieveOperation(path="foo", returns=BaseSchemaStruct)

    assert operation


def test_retrieve_operation_instantiates_for_paths_with_declared_arguments():
    class OperationArgs(PathArgs):
        id: int

    operation = RetrieveOperation(
        path="collection/{id}/sub-resource",
        call_args=OperationArgs,
        returns=BaseSchemaStruct,
    )

    assert operation


def test_retrieve_operation_raises_for_mismatch_in_path_and_args_params():
    with pytest.raises(
        TypeError,
        match="path 'foo/{bar}' expects path parameters bar, which is not declared",
    ):
        RetrieveOperation(path="foo/{bar}", returns=BaseSchemaStruct)


def test_retrieve_operation_raises_for_positional_args():
    class Args:
        def __init__(self, pos_arg: int):
            pass

    with pytest.raises(TypeError, match="must only accept keyword arguments"):
        RetrieveOperation(path="{pos_arg}", call_args=Args, returns=BaseSchemaStruct)
