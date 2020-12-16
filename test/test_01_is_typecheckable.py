""" Tests for `typing_json.typechecking.is_typecheckable` """
# pylint: disable = line-too-long, invalid-name, missing-docstring

# standard imports
from typing import Union, Optional, List, Tuple, Set, FrozenSet, Mapping, Dict, OrderedDict, NamedTuple

# external dependencies
from typing_extensions import Literal, TypedDict

# internal imports
from typing_json.typechecking import is_typecheckable, TYPECHECKABLE_BASE_TYPES


def failure_callback(message: str) -> None:
    print(message)


def test_is_typecheckable_basetypes1():
    """
        Tests that base types which are meant
        to be typecheckable are actually typecheckable.
    """
    for t in TYPECHECKABLE_BASE_TYPES:
        assert is_typecheckable(t, failure_callback=failure_callback)
    assert is_typecheckable(None, failure_callback=failure_callback)


def test_is_typecheckable_basetypes2():
    """
        Tests that types which are not meant to be
        typecheckable are not typecheckable.
    """
    class NonTypechekableT:
        name: str
        val: int
    assert not is_typecheckable(NonTypechekableT, failure_callback=failure_callback)


def test_is_typecheckable_enums():
    """
        Tests that enums are typecheckable.
    """
    from enum import Enum
    class Color(Enum):
        # pylint:disable=all
        Red = 0
        Green = 1
        Blue = 2
    assert is_typecheckable(Color, failure_callback=failure_callback)


def test_is_typecheckable_collections1():
    """
        Tests that collections of typecheckable base types
        are typecheckable.
    """
    for t in TYPECHECKABLE_BASE_TYPES:
        assert is_typecheckable(FrozenSet[t], failure_callback=failure_callback)
        assert is_typecheckable(Union[t, Tuple[t]], failure_callback=failure_callback)
        assert is_typecheckable(Optional[t], failure_callback=failure_callback)
        assert is_typecheckable(Tuple[t, ...], failure_callback=failure_callback)
        assert is_typecheckable(Tuple[t], failure_callback=failure_callback)
        assert is_typecheckable(Tuple[t, int], failure_callback=failure_callback)
        assert is_typecheckable(Tuple[t, int, str], failure_callback=failure_callback)
        assert is_typecheckable(Set[t], failure_callback=failure_callback)
        assert is_typecheckable(List[t], failure_callback=failure_callback)
        assert is_typecheckable(Dict[str, t], failure_callback=failure_callback)
        assert is_typecheckable(Dict[t, int], failure_callback=failure_callback)
        assert is_typecheckable(OrderedDict[str, t], failure_callback=failure_callback)
        assert is_typecheckable(OrderedDict[t, int], failure_callback=failure_callback)
        assert is_typecheckable(Mapping[str, t], failure_callback=failure_callback)
        assert is_typecheckable(Mapping[t, int], failure_callback=failure_callback)


def test_is_typecheckable_collections2():
    """
        Tests that collections of non-typecheckable
        types are not typecheckable.
    """
    class NonTypechekableT:
        name: str
        val: int
    assert not is_typecheckable(FrozenSet[NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(Union[NonTypechekableT, Tuple[int]], failure_callback=failure_callback)
    assert not is_typecheckable(Optional[NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(Tuple[NonTypechekableT, ...], failure_callback=failure_callback)
    assert not is_typecheckable(Tuple[NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(Tuple[NonTypechekableT, int], failure_callback=failure_callback)
    assert not is_typecheckable(Set[NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(List[NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(Dict[str, NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(Dict[NonTypechekableT, int], failure_callback=failure_callback)
    assert not is_typecheckable(OrderedDict[str, NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(OrderedDict[NonTypechekableT, int], failure_callback=failure_callback)
    assert not is_typecheckable(Mapping[str, NonTypechekableT], failure_callback=failure_callback)
    assert not is_typecheckable(Mapping[NonTypechekableT, int], failure_callback=failure_callback)


def test_is_typecheckable_literal():
    """
        Tests that literals are typecheckable.
    """
    assert is_typecheckable(Literal["hi", 1, 2.5])


def test_is_typecheckable_namedtuple():
    """
        Tests that namedtuples are typecheckable if
        and only if their attributes are of typecheckable type.
    """
    class HashableNamedTupleExampleT(NamedTuple):
        name: Tuple[str, ...]
        value: Union[int, float]
    assert is_typecheckable(HashableNamedTupleExampleT, failure_callback=failure_callback)
    class NonHashableNamedTupleExampleT(NamedTuple):
        name: List[str]
        value: Union[int, float]
    assert is_typecheckable(NonHashableNamedTupleExampleT, failure_callback=failure_callback)
    class NonTypechekableT:
        name: str
        val: int
    class NonTypecheckableNamedTupleExampleT(NamedTuple):
        name: List[NonTypechekableT]
        value: Union[int, float]
    assert not is_typecheckable(NonTypecheckableNamedTupleExampleT, failure_callback=failure_callback)

def test_is_typecheckable_typed_dict():
    """
        Tests that typed dicts are typecheckable if
        and only if their attributes are of typecheckable type.
    """
    class TypedDictExample1T(TypedDict):
        name: Tuple[str, ...]
        value: Union[int, float]
    assert is_typecheckable(TypedDictExample1T, failure_callback=failure_callback)
    class TypedDictExample2T(TypedDict):
        name: List[str] = ["Hello"]
        value: Union[int, float]
    assert is_typecheckable(TypedDictExample2T, failure_callback=failure_callback)
    class NonTypechekableT:
        name: str
        val: int
    class NonTypecheckableTypedDictExample1T(TypedDict):
        name: List[NonTypechekableT]
        value: Union[int, float]
    assert not is_typecheckable(NonTypecheckableTypedDictExample1T, failure_callback=failure_callback)
    class NonTypecheckableTypedDictExample2T(TypedDict):
        name: str = 10
        value: Union[int, float]
    assert not is_typecheckable(NonTypecheckableTypedDictExample2T, failure_callback=failure_callback)
