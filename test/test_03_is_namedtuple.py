""" Tests for `typing_json.typechecking.is_namedtuple` """
# pylint: disable = line-too-long, invalid-name, missing-docstring

# standard imports
import sys
import typing
from typing import Any, Union, Optional, List, Tuple, Set, FrozenSet, Mapping, Dict, NamedTuple, Deque
from collections import namedtuple, deque, OrderedDict
from decimal import Decimal

# external dependencies
from typing_extensions import Literal

# internal imports
from typing_json.typechecking import is_namedtuple, is_instance, TYPECHECKABLE_BASE_TYPES


def failure_callback(message: str) -> None:
    print(message)

def test_is_namedtuple_basic():
    """
        Tests that `typing.NamedTuple` are identified correctly,
        while classes, `tuple` and `namedtuple` are not.
    """
    class A(NamedTuple):
        # pylint:disable=all
        name: List[str]
        value: Union[int, float]
    assert is_namedtuple(A, failure_callback=failure_callback)
    a = A(["hi"], 1.1)
    assert is_instance(a, A, failure_callback=failure_callback)
    a = A(0, 1.1) # type:ignore
    assert not is_instance(a, A, failure_callback=failure_callback)
    a = A(["hi"], 1.1)
    class B:
        # pylint:disable=all
        name: List[str]
        def __init__(self, name: List[str]):
            self.name = name
    class Btuple(tuple):
        # pylint:disable=all
        name: List[str]
        def __init__(self, name: List[str]):
            self.name = name
    assert not is_namedtuple(0, failure_callback=failure_callback)
    assert not is_namedtuple(B, failure_callback=failure_callback)
    assert not is_namedtuple(Btuple, failure_callback=failure_callback)
    b = B(["hi"])
    assert not is_instance(b, A, failure_callback=failure_callback)
    C = namedtuple("C", ["name", "value"])
    assert not is_namedtuple(C, failure_callback=failure_callback)

def test_is_namedtuple_fake1():
    """
        Tries to make a fake namedtuple by adding `_field_types`
        to a `tuple`.

        Note: for some odd reason the following test fails in 3.7.1,
        so this test is only executed in Python 3.7.4+.
    """
    C = namedtuple("C", ["name", "value"])
    version_info = sys.version_info
    if version_info[0:3]>= (3, 7, 4):
        C._field_types = {"name": str, "value": int}
        assert is_namedtuple(C, failure_callback=failure_callback)

def test_is_namedtuple_fake2():
    """
        Tries to make a fake `typing.NamedTuple` by adding `_fields`
        to a `tuple`.
    """
    class D1(tuple):
        _fields = []
    assert not is_namedtuple(D1, failure_callback=failure_callback)
    class D2(tuple):
        _fields = ("name", 0)
    assert not is_namedtuple(D2, failure_callback=failure_callback)

def test_is_namedtuple_fake3():
    """
        Tries to make a fake `typing.NamedTuple` by adding
        `_fields` and `_field_types` to a `tuple`,
        but getting things slightly wrong.
    """
    class B:
        # pylint:disable=all
        name: List[str]
        def __init__(self, name: List[str]):
            self.name = name
    class D3(tuple):
        _fields = ("name", "value")
        _field_types = []
    assert not is_namedtuple(D3, failure_callback=failure_callback)
    class D4(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "val": int}
    assert not is_namedtuple(D4, failure_callback=failure_callback)
    class D5(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "value": int, "val": int}
    assert not is_namedtuple(D5, failure_callback=failure_callback)
    class D6(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "value": B}
    assert not is_namedtuple(D6, failure_callback=failure_callback)
    class D6prime(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "value": int}
    assert not is_namedtuple(D6prime, failure_callback=failure_callback)

def test_is_namedtuple_fake4():
    """
        Tries to make a fake `typing.NamedTuple` by adding
        `_fields`, `_field_types` and `_field_defaults` to a `tuple`,
        but getting things slightly wrong.
    """
    class D7(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "value": int}
        _field_defaults = []
    assert not is_namedtuple(D7, failure_callback=failure_callback)
    class D8(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "value": int}
        _field_defaults = {"val": 0}
    assert not is_namedtuple(D8, failure_callback=failure_callback)
    class D9(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "value": int}
        _field_defaults = {"value": "bye"}
    assert not is_namedtuple(D9, failure_callback=failure_callback)

def test_is_namedtuple_fake5():
    """
        Tries to make a fake `typing.NamedTuple` by adding
        `_fields`, `_field_types` and `_field_defaults` to a `tuple`,
        but forgets to add the actual fields to the class.
    """
    class A(NamedTuple):
        # pylint:disable=all
        name: str = "a"
        value: int = 0
    assert is_namedtuple(A, failure_callback=failure_callback)
    class FakeA(tuple):
        _fields = ("name", "value")
        _field_types = {"name": str, "value": int}
        _field_defaults = {"name": "a", "value": 0}
    assert not is_namedtuple(FakeA, failure_callback=failure_callback)

def test_is_namedtuple_fake6():
    """
        Tries to make a fake `typing.NamedTuple` by adding
        `_fields`, `_field_types` and `_field_defaults` to a `tuple`
        and adding the actual fields to the class.
        Unfortunately, the fields don't get added to `dir` for a `tuple`.
    """
    class A(NamedTuple):
        # pylint:disable=all
        name: str = "a"
        value: int = 0
    assert is_namedtuple(A, failure_callback=failure_callback)
    class FakeA(tuple):
        name: str
        value: int
        _fields = ("name", "value")
        _field_types = {"name": str, "value": int}
        _field_defaults = {"name": "a", "value": 0}
    assert not is_namedtuple(FakeA, failure_callback=failure_callback)
