""" Tests for `typing_json.typechecking.is_keyable` """
# pylint: disable = line-too-long, invalid-name, missing-docstring

# standard imports
from typing import Union, Optional, List, Tuple, Set, FrozenSet, Mapping, Dict, OrderedDict, NamedTuple

# external dependencies
from typing_extensions import Literal

# internal imports
from typing_json.typechecking import is_keyable, KEYABLE_BASE_TYPES, TYPECHECKABLE_BASE_TYPES


NONKEYABLE_BASE_TYPES = tuple(t for t in TYPECHECKABLE_BASE_TYPES if t not in KEYABLE_BASE_TYPES)


def failure_callback(message: str) -> None:
    print(message)


def test_is_keyable_basetypes1():
    """
        Tests that base types which are meant
        to be keyable are actually keyable.
    """
    for t in KEYABLE_BASE_TYPES:
        assert is_keyable(t, failure_callback=failure_callback)
    assert is_keyable(None, failure_callback=failure_callback)


def test_is_keyable_basetypes2():
    """
        Tests that base types which are not meant
        to be keyable are actually not keyable.
    """
    for t in NONKEYABLE_BASE_TYPES:
        assert not is_keyable(t, failure_callback=failure_callback)


def test_is_keyable_enums():
    """
        Tests that enums are keyable.
    """
    from enum import Enum
    class Color(Enum):
        # pylint:disable=all
        Red = 0
        Green = 1
        Blue = 2
    assert is_keyable(Color, failure_callback=failure_callback)


def test_is_keyable_collections1():
    """
        Tests that keyable collections of
        keyable base types are keyable.
    """
    for t in KEYABLE_BASE_TYPES:
        assert is_keyable(FrozenSet[t], failure_callback=failure_callback)
        assert is_keyable(Union[t, Tuple[t]], failure_callback=failure_callback)
        assert is_keyable(Optional[t], failure_callback=failure_callback)
        assert is_keyable(Tuple[t, ...], failure_callback=failure_callback)
        assert is_keyable(Tuple[t], failure_callback=failure_callback)
        assert is_keyable(Tuple[t, int], failure_callback=failure_callback)
        assert is_keyable(Tuple[t, int, str], failure_callback=failure_callback)


def test_is_keyable_collections2():
    """
        Tests that non-keyable collections of
        keyable base types are not keyable.
    """
    for t in TYPECHECKABLE_BASE_TYPES:
        assert not is_keyable(Set[t], failure_callback=failure_callback)
        assert not is_keyable(List[t], failure_callback=failure_callback)
        assert not is_keyable(Dict[str, t], failure_callback=failure_callback)
        assert not is_keyable(Dict[t, int], failure_callback=failure_callback)
        assert not is_keyable(OrderedDict[str, t], failure_callback=failure_callback)
        assert not is_keyable(OrderedDict[t, int], failure_callback=failure_callback)
        assert not is_keyable(Mapping[str, t], failure_callback=failure_callback)
        assert not is_keyable(Mapping[t, int], failure_callback=failure_callback)


def test_is_keyable_collections3():
    """
        Tests that keyable collections of
        non-keyable base types are not keyable.
    """
    for t in NONKEYABLE_BASE_TYPES:
        assert not is_keyable(FrozenSet[t], failure_callback=failure_callback)
        assert not is_keyable(Union[t, Tuple[t]], failure_callback=failure_callback)
        assert not is_keyable(Optional[t], failure_callback=failure_callback)
        assert not is_keyable(Tuple[t, ...], failure_callback=failure_callback)
        assert not is_keyable(Tuple[t], failure_callback=failure_callback)
        assert not is_keyable(Tuple[t, int], failure_callback=failure_callback)
        assert not is_keyable(Tuple[t, int, str], failure_callback=failure_callback)


def test_is_keyable_literal():
    """
        Tests that literals are keyable.
    """
    assert is_keyable(Literal["hi", 1, 2.5])


def test_is_keyable_namedtuple():
    """
        Tests that namedtuples are keyable
        if and only if they have keyable
        field type.
    """
    class HashableNamedTupleExampleT(NamedTuple):
        name: Tuple[str, ...]
        value: Union[int, float]
    assert is_keyable(HashableNamedTupleExampleT, failure_callback=failure_callback)
    class NonHashableNamedTupleExampleT(NamedTuple):
        name: List[str]
        value: Union[int, float]
    assert not is_keyable(NonHashableNamedTupleExampleT, failure_callback=failure_callback)
