""" Tests for `typing_json.typechecking.is_typed_dict` """
# pylint: disable = line-too-long, invalid-name, missing-docstring

# standard imports
import sys
import typing
from typing import Any, Union, Optional, List, Tuple, Set, FrozenSet, Mapping, Dict, TypedDict, Deque
from collections import namedtuple, deque, OrderedDict
from decimal import Decimal

# external dependencies
from typing_extensions import Literal, TypedDict

# internal imports
from typing_json.typechecking import is_typed_dict, is_instance, TYPECHECKABLE_BASE_TYPES


def failure_callback(message: str) -> None:
    print(message)

def test_is_typed_dict_basic():
    """
        Tests that `typing.TypedDict` are identified correctly,
        while classes and `dict` are not.
    """
    class A(TypedDict):
        # pylint:disable=all
        name: List[str]
        value: Union[int, float]
    assert is_typed_dict(A, failure_callback=failure_callback)
    a = {"name": ["hi"], "value": 1.1}
    assert is_instance(a, A, failure_callback=failure_callback)
    a = {"name": 0, "value": 1.1} # type:ignore
    assert not is_instance(a, A, failure_callback=failure_callback)
    a = {"name": ["hi"], "value": 1.1}
    class B:
        # pylint:disable=all
        name: List[str]
        def __init__(self, name: List[str]):
            self.name = name
    assert not is_typed_dict(0, failure_callback=failure_callback)
    assert not is_typed_dict(B, failure_callback=failure_callback)
    assert not is_typed_dict(dict, failure_callback=failure_callback)
    b = B(["hi"])
    assert not is_instance(b, A, failure_callback=failure_callback)

def test_is_typed_dict_fake1():
    """
        Tries to make a fake typed dict
    """
    class C:
        ...
    assert not is_typed_dict(C, failure_callback=failure_callback)

def test_is_typed_dict_fake2():
    """
        Tries to make a fake typed dict
    """
    class C(dict):
        ...
    assert not is_typed_dict(C, failure_callback=failure_callback)

def test_is_typed_dict_fake3():
    """
        Tries to make a fake typed dict
    """
    class C(dict):
        ...
    C.__annotations__ = "hello"
    assert not is_typed_dict(C, failure_callback=failure_callback)

def test_is_typed_dict_fake4():
    """
        Tries to make a fake typed dict
    """
    class C(dict):
        ...
    C.__annotations__ = {}
    assert not is_typed_dict(C, failure_callback=failure_callback)

def test_is_typed_dict_fake5():
    """
        Tries to make a fake typed dict
    """
    class C(dict):
        ...
    C.__annotations__ = {}
    C.__total__ = "hello"
    assert not is_typed_dict(C, failure_callback=failure_callback)

def test_is_typed_dict_fake6():
    """
        Tries to make a fake typed dict
    """
    class C(dict):
        ...
    C.__annotations__ = {
        "name": int
    }
    C.__total__ = True
    C.name = "bye"
    assert not is_typed_dict(C, failure_callback=failure_callback)

def test_is_typed_dict_fake7():
    """
        Tries to make a fake typed dict
    """
    class C(dict):
        ...
    C.__annotations__ = {
        10: int
    }
    C.__total__ = True
    C.name = "bye"
    assert not is_typed_dict(C, failure_callback=failure_callback)
