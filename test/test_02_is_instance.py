""" Tests for `typing_json.typechecking.is_instance` """
# pylint: disable = line-too-long, invalid-name, missing-docstring

# standard imports
import typing
from typing import Any, Union, Optional, List, Tuple, Set, FrozenSet, Mapping, Dict, NamedTuple, Deque
from collections import deque, OrderedDict
from decimal import Decimal

# external dependencies
from typing_extensions import Literal

# internal imports
from typing_json.typechecking import is_instance, TYPECHECKABLE_BASE_TYPES


def failure_callback(message: str) -> None:
    print(message)


def test_is_instance_basetypes1():
    """
        Checks that values which should be instances of
        basic types are actually recognised as instances.
    """
    values = {
        bool: True,
        int: 1,
        float: 1.0,
        complex: 1.0j,
        str: "hello",
        bytes: b"hello",
        bytearray: bytearray(b"hello"),
        memoryview: memoryview(b"hello"),
        list: ["hello", 0],
        tuple: ("hello", 0),
        range: range(15),
        slice: slice(15),
        set: set(["hello", 0]),
        frozenset: frozenset(["hello", 0]),
        dict: {"str": "hello", "int": 0},
        type: str,
        None: None,
        Decimal: Decimal('1.0'),
    }
    for t, obj in values.items():
        assert is_instance(obj, t, failure_callback=failure_callback)
        assert is_instance(obj, Any, failure_callback=failure_callback)

def test_is_instance_basetypes2():
    """
        Checks that values which should not be instances of
        basic types are actually not recognised as instances.
    """
    values = {
        bool: "False", # bool inherits from int, see https://www.python.org/dev/peps/pep-0285/
        int: "1",
        float: "1.0",
        complex: "1.0j",
        str: 1,
        bytes: "hello",
        bytearray: "hello",
        memoryview: "hello",
        list: ("hello", 0),
        tuple: ["hello", 0],
        range: slice(15),
        slice: range(15),
        set: frozenset(["hello", 0]),
        frozenset: set(["hello", 0]),
        dict: ["str", "hello", "int",  0],
        type: 1,
        None: 1,
        Decimal: 1.0,
    }
    for t, obj in values.items():
        assert not is_instance(obj, t, failure_callback=failure_callback)


def test_is_instance_bool():
    """
        Tests `is_instance` specifically on `bool` and `int`.
        The issue is that `bool` inherits from `int`,
        see https://www.python.org/dev/peps/pep-0285/
    """
    assert not is_instance(True, int)
    assert not is_instance(False, int)
    assert not is_instance(0, bool)
    assert not is_instance(1, bool)


def test_is_instance_enums():
    """ Tests `is_instance` on enums. """
    from enum import Enum
    class Color(Enum):
        # pylint:disable=all
        Red = 0
        Green = 1
        Blue = 2
    class Shape(Enum):
        # pylint:disable=all
        Circle = 0
        Square = 1
    assert is_instance(Color.Red, Color, failure_callback=failure_callback)
    assert not is_instance(0, Color, failure_callback=failure_callback)
    assert not is_instance(Shape.Circle, Color, failure_callback=failure_callback)


def test_is_instance_namedtuple():
    """ Tests `is_instance` on namedtuples. """
    class NamedTupleExample1T(NamedTuple):
        # pylint:disable=all
        name: str
        value: int
    class NamedTupleExample2T(NamedTuple):
        # pylint:disable=all
        name: str
        value: int
    class ClassExampleT:
        # pylint:disable=all
        name: str
        value: int
        def __init__(self, name, value):
            self.name = name
            self.value = value
    t1 = NamedTupleExample1T("t1", 1)
    t2 = NamedTupleExample2T("t2", 1)
    c = ClassExampleT("c", 1)
    assert is_instance(t1, NamedTupleExample1T, failure_callback=failure_callback)
    assert not is_instance(t2, NamedTupleExample1T, failure_callback=failure_callback)
    assert not is_instance(c, NamedTupleExample1T, failure_callback=failure_callback)
    assert not is_instance(t1._replace(value="1"), NamedTupleExample1T, failure_callback=failure_callback)


def test_is_instance_union():
    """ Tests `is_instance` on unions and optional types. """
    assert is_instance(True, Optional[bool], failure_callback=failure_callback)
    assert is_instance(None, Optional[bool], failure_callback=failure_callback)
    assert not is_instance("hi", Optional[bool], failure_callback=failure_callback)
    assert is_instance(1, Union[int, str], failure_callback=failure_callback)
    assert is_instance("hi", Union[int, str], failure_callback=failure_callback)
    assert not is_instance(range(15), Union[int, str], failure_callback=failure_callback)


def test_is_instance_literal():
    """ Tests `is_instance` on literal types. """
    assert is_instance("hi", Literal["hi", 1, 2.5], failure_callback=failure_callback)
    assert is_instance(1, Literal["hi", 1, 2.5], failure_callback=failure_callback)
    assert is_instance(2.5, Literal["hi", 1, 2.5], failure_callback=failure_callback)
    assert not is_instance("hello", Literal["hi", 1, 2.5], failure_callback=failure_callback)
    assert not is_instance(2, Literal["hi", 1, 2.5], failure_callback=failure_callback)
    assert not is_instance(1.5, Literal["hi", 1, 2.5], failure_callback=failure_callback)


def test_is_instance_list():
    """ Tests `is_instance` on lists. """
    assert is_instance([], List[int], failure_callback=failure_callback)
    assert is_instance([0, 1, 2], List[int], failure_callback=failure_callback)
    assert not is_instance((0, 1, 2), List[int], failure_callback=failure_callback)
    assert not is_instance([0, 1, "2"], List[int], failure_callback=failure_callback)
    assert is_instance([0, 1, "2"], List[Union[int, str]], failure_callback=failure_callback)


def test_is_instance_tuple1():
    """ Tests `is_instance` on variadic tuples. """
    assert is_instance(tuple(), Tuple[int, ...], failure_callback=failure_callback)
    assert is_instance((0, 1, 2), Tuple[int, ...], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], Tuple[int, ...], failure_callback=failure_callback)
    assert not is_instance((0, 1, "2"), Tuple[int, ...], failure_callback=failure_callback)
    assert is_instance((0, 1, "2"), Tuple[Union[int, str], ...], failure_callback=failure_callback)


def test_is_instance_tuple2():
    """ Tests `is_instance` on fixed-length tuples. """
    assert not is_instance(tuple(), Tuple[int, int, int], failure_callback=failure_callback)
    assert not is_instance((0, 1), Tuple[int, int, int], failure_callback=failure_callback)
    assert is_instance((0, 1, 2), Tuple[int, int, int], failure_callback=failure_callback)
    assert not is_instance((0, 1, 2, 3), Tuple[int, int, int], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], Tuple[int, int, int], failure_callback=failure_callback)
    assert not is_instance((0, 1, "2"), Tuple[int, int, int], failure_callback=failure_callback)
    assert is_instance((0, 1, "2"), Tuple[int, int, str], failure_callback=failure_callback)


def test_is_instance_set():
    """ Tests `is_instance` on sets. """
    assert is_instance(set(), Set[int], failure_callback=failure_callback)
    assert is_instance({0, 1, 2}, Set[int], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], Set[int], failure_callback=failure_callback)
    assert not is_instance({0, 1, "2"}, Set[int], failure_callback=failure_callback)
    assert is_instance({0, 1, "2"}, Set[Union[int, str]], failure_callback=failure_callback)


def test_is_instance_frozenset():
    """ Tests `is_instance` on frozensets. """
    assert is_instance(frozenset(), FrozenSet[int], failure_callback=failure_callback)
    assert is_instance(frozenset({0, 1, 2}), FrozenSet[int], failure_callback=failure_callback)
    assert not is_instance({0, 1, 2}, FrozenSet[int], failure_callback=failure_callback)
    assert not is_instance(frozenset({0, 1, "2"}), FrozenSet[int], failure_callback=failure_callback)
    assert is_instance(frozenset({0, 1, "2"}), FrozenSet[Union[int, str]], failure_callback=failure_callback)


def test_is_instance_deque():
    """ Tests `is_instance` on dequeues. """
    assert is_instance(deque(), Deque[int], failure_callback=failure_callback)
    assert is_instance(deque([0, 1, 2]), Deque[int], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], Deque[int], failure_callback=failure_callback)
    assert not is_instance(deque([0, 1, "2"]), Deque[int], failure_callback=failure_callback)
    assert is_instance(deque([0, 1, "2"]), Deque[Union[int, str]], failure_callback=failure_callback)


def test_is_instance_dict():
    """ Tests `is_instance` on dictionaries. """
    assert is_instance(dict(), Dict[str, int], failure_callback=failure_callback)
    assert is_instance({"0": 0, "1": 1, "2": 2}, Dict[str, int], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], Dict[str, int], failure_callback=failure_callback)
    assert not is_instance({"0": 0, "1": 1, "2": "2"}, Dict[str, int], failure_callback=failure_callback)
    assert not is_instance({"0": 0, "1": 1, 2: 2}, Dict[str, int], failure_callback=failure_callback)
    assert is_instance({"0": 0, "1": 1, "2": "2"}, Dict[str, Union[str, int]], failure_callback=failure_callback)
    assert is_instance({"0": 0, "1": 1, 2: 2}, Dict[Union[str, int], int], failure_callback=failure_callback)


def test_is_instance_ordereddict():
    """ Tests `is_instance` on ordered dictionaries. """
    assert is_instance(OrderedDict(), typing.OrderedDict[str, int], failure_callback=failure_callback)
    assert is_instance(OrderedDict({"0": 0, "1": 1, "2": 2}), typing.OrderedDict[str, int], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], typing.OrderedDict[str, int], failure_callback=failure_callback)
    assert not is_instance(OrderedDict({"0": 0, "1": 1, "2": "2"}), typing.OrderedDict[str, int], failure_callback=failure_callback)
    assert not is_instance(OrderedDict({"0": 0, "1": 1, 2: 2}), typing.OrderedDict[str, int], failure_callback=failure_callback)
    assert is_instance(OrderedDict({"0": 0, "1": 1, "2": "2"}), typing.OrderedDict[str, Union[str, int]], failure_callback=failure_callback)
    assert is_instance(OrderedDict({"0": 0, "1": 1, 2: 2}), typing.OrderedDict[Union[str, int], int], failure_callback=failure_callback)


def test_is_instance_mapping():
    """ Tests `is_instance` on read-only dictionaries. """
    # dict
    assert is_instance(dict(), Mapping[str, int], failure_callback=failure_callback)
    assert is_instance({"0": 0, "1": 1, "2": 2}, Mapping[str, int], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], Mapping[str, int], failure_callback=failure_callback)
    assert not is_instance({"0": 0, "1": 1, "2": "2"}, Mapping[str, int], failure_callback=failure_callback)
    assert not is_instance({"0": 0, "1": 1, 2: 2}, Mapping[str, int], failure_callback=failure_callback)
    assert is_instance({"0": 0, "1": 1, "2": "2"}, Mapping[str, Union[str, int]], failure_callback=failure_callback)
    assert is_instance({"0": 0, "1": 1, 2: 2}, Mapping[Union[str, int], int], failure_callback=failure_callback)
    # OrderedDict
    assert is_instance(OrderedDict(), Mapping[str, int], failure_callback=failure_callback)
    assert is_instance(OrderedDict({"0": 0, "1": 1, "2": 2}), Mapping[str, int], failure_callback=failure_callback)
    assert not is_instance([0, 1, 2], Mapping[str, int], failure_callback=failure_callback)
    assert not is_instance(OrderedDict({"0": 0, "1": 1, "2": "2"}), Mapping[str, int], failure_callback=failure_callback)
    assert not is_instance(OrderedDict({"0": 0, "1": 1, 2: 2}), Mapping[str, int], failure_callback=failure_callback)
    assert is_instance(OrderedDict({"0": 0, "1": 1, "2": "2"}), Mapping[str, Union[str, int]], failure_callback=failure_callback)
    assert is_instance(OrderedDict({"0": 0, "1": 1, 2: 2}), Mapping[Union[str, int], int], failure_callback=failure_callback)


def test_is_instance_unsupported_type():
    class C:
        # pylint: disable = all
        name: str
        value: int
        def __init__(self, name: str, value: int):
            self.name = name
            self.value = value
    c = C("c", 0)
    try:
        is_instance(c, C, failure_callback=failure_callback)
        assert False
    except TypeError:
        assert True

def test_is_instance_decimal1():
    assert is_instance(Decimal("1.0"), int, failure_callback=failure_callback, cast_decimal=True)
    assert is_instance(Decimal(1.0), int, failure_callback=failure_callback, cast_decimal=True)
    assert is_instance(Decimal("1"), int, failure_callback=failure_callback, cast_decimal=True)
    assert is_instance(Decimal(1), int, failure_callback=failure_callback, cast_decimal=True)

def test_is_instance_decimal2():
    assert not is_instance(Decimal("1.0"), int, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal(1.0), int, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal("1"), int, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal(1), int, failure_callback=failure_callback, cast_decimal=False)

def test_is_instance_decimal3():
    assert not is_instance(Decimal("1.1"), int, failure_callback=failure_callback, cast_decimal=True)
    assert not is_instance(Decimal(1.000000000000001), int, failure_callback=failure_callback, cast_decimal=True)
    assert is_instance(Decimal("1.1"), float, failure_callback=failure_callback, cast_decimal=True)
    assert is_instance(Decimal(1.000000000000001), float, failure_callback=failure_callback, cast_decimal=True)
    assert is_instance(Decimal("1.0"), float, failure_callback=failure_callback, cast_decimal=True)
    assert is_instance(Decimal(1), float, failure_callback=failure_callback, cast_decimal=True)

def test_is_instance_decimal5():
    assert not is_instance(Decimal("1.1"), int, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal(1.000000000000001), int, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal("1.1"), float, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal(1.000000000000001), float, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal("1.0"), float, failure_callback=failure_callback, cast_decimal=False)
    assert not is_instance(Decimal(1), float, failure_callback=failure_callback, cast_decimal=False)
