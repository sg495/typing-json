""" Tests for `typing_json.typechecking.is_json_encodable` """
# pylint: disable = line-too-long, invalid-name, missing-docstring

# standard imports
from typing import Union, Optional, List, Tuple, Set, FrozenSet, Mapping, Dict, OrderedDict, NamedTuple
from decimal import Decimal

# external dependencies
from typing_extensions import Literal, TypedDict

# internal imports
from typing_json.typechecking import TYPECHECKABLE_BASE_TYPES
from typing_json.encoding import is_json_encodable, JSON_BASE_TYPES


NONENCODABLE_BASE_TYPES = tuple(t for t in TYPECHECKABLE_BASE_TYPES if t not in JSON_BASE_TYPES+(Decimal,))

def failure_callback(message: str) -> None:
    print(message)


def test_is_json_encodable_basetypes():
    """
        Tests that base types which are meant
        to be JSON encodable are actually JSON encodable.
    """
    for t in JSON_BASE_TYPES:
        assert is_json_encodable(t, failure_callback=failure_callback)
    assert is_json_encodable(None, failure_callback=failure_callback)
    assert is_json_encodable(Decimal, failure_callback=failure_callback)

def test_is_json_encodable_classes():
    """
        Tests that some types which are not meant
        to be JSON encodable are actually not JSON encodable.
    """
    class t:
        # pylint: disable = all
        name: str
        value: int
    assert not is_json_encodable(t, failure_callback=failure_callback)


def test_is_json_encodable_enums():
    """
        Tests that enums are JSON encodable.
    """
    from enum import Enum
    class Color(Enum):
        # pylint:disable=all
        Red = 0
        Green = 1
        Blue = 2
    assert is_json_encodable(Color, failure_callback=failure_callback)


def test_is_json_encodable_collections1():
    """
        Tests that collections of JSON base types, `decimal.Decimal`
        and enums are typecheckable.
    """
    from enum import Enum
    class Color(Enum):
        # pylint:disable=all
        Red = 0
        Green = 1
        Blue = 2
    for t in JSON_BASE_TYPES+(Decimal, Color):
        assert is_json_encodable(FrozenSet[t], failure_callback=failure_callback)
        assert is_json_encodable(Union[t, Tuple[t]], failure_callback=failure_callback)
        assert is_json_encodable(Optional[t], failure_callback=failure_callback)
        assert is_json_encodable(Tuple[t, ...], failure_callback=failure_callback)
        assert is_json_encodable(Tuple[t], failure_callback=failure_callback)
        assert is_json_encodable(Tuple[t, int], failure_callback=failure_callback)
        assert is_json_encodable(Tuple[t, int, str], failure_callback=failure_callback)
        assert is_json_encodable(Set[t], failure_callback=failure_callback)
        assert is_json_encodable(List[t], failure_callback=failure_callback)
        assert is_json_encodable(Dict[str, t], failure_callback=failure_callback)
        assert is_json_encodable(Dict[t, int], failure_callback=failure_callback)
        assert is_json_encodable(OrderedDict[str, t], failure_callback=failure_callback)
        assert is_json_encodable(OrderedDict[t, int], failure_callback=failure_callback)
        assert is_json_encodable(Mapping[str, t], failure_callback=failure_callback)
        assert is_json_encodable(Mapping[t, int], failure_callback=failure_callback)


def test_is_json_encodable_collections2():
    """
        Tests that collections of non-typecheckable
        types are not typecheckable.
    """
    for t in NONENCODABLE_BASE_TYPES:
        assert not is_json_encodable(FrozenSet[t], failure_callback=failure_callback)
        assert not is_json_encodable(Union[t, Tuple[int]], failure_callback=failure_callback)
        assert not is_json_encodable(Optional[t], failure_callback=failure_callback)
        assert not is_json_encodable(Tuple[t, ...], failure_callback=failure_callback)
        assert not is_json_encodable(Tuple[t], failure_callback=failure_callback)
        assert not is_json_encodable(Tuple[t, int], failure_callback=failure_callback)
        assert not is_json_encodable(Set[t], failure_callback=failure_callback)
        assert not is_json_encodable(List[t], failure_callback=failure_callback)
        assert not is_json_encodable(Dict[str, t], failure_callback=failure_callback)
        assert not is_json_encodable(Dict[t, int], failure_callback=failure_callback)
        assert not is_json_encodable(OrderedDict[str, t], failure_callback=failure_callback)
        assert not is_json_encodable(OrderedDict[t, int], failure_callback=failure_callback)
        assert not is_json_encodable(Mapping[str, t], failure_callback=failure_callback)
        assert not is_json_encodable(Mapping[t, int], failure_callback=failure_callback)



def test_is_json_encodable_literal():
    """
        Tests that Literal types are JSON encodable if and only if all
        literals are of JSON base type or `decimal.Decimal`.
    """
    assert is_json_encodable(Literal["hello", 1, 2.5, None], failure_callback=failure_callback)
    assert not is_json_encodable(Literal["hello", 1, 2.5, None, 1+1j], failure_callback=failure_callback)

def test_is_json_encodable_namedtuple():
    """
        Tests that namedtuples are JSON encodable if
        and only if their attributes are of JSON encodable type.
    """
    class HashableNamedTupleExampleT(NamedTuple):
        name: Tuple[str, ...]
        value: Union[int, float]
    assert is_json_encodable(HashableNamedTupleExampleT, failure_callback=failure_callback)
    class NonHashableNamedTupleExampleT(NamedTuple):
        name: List[str]
        value: Union[int, float, complex]
    assert not is_json_encodable(NonHashableNamedTupleExampleT, failure_callback=failure_callback)
    class NonTypechekableT:
        name: str
        val: int
    class NonTypecheckableNamedTupleExampleT(NamedTuple):
        name: List[NonTypechekableT]
        value: Union[int, float]
    assert not is_json_encodable(NonTypecheckableNamedTupleExampleT, failure_callback=failure_callback)


def test_is_json_encodable_typed_dict():
    """
        Tests that typed dicts are typecheckable if
        and only if their attributes are of JSON encodable type.
    """
    class TypedDictExample1T(TypedDict):
        name: Tuple[str, ...]
        value: Union[int, float]
    assert is_json_encodable(TypedDictExample1T, failure_callback=failure_callback)
    class TypedDictExample2T(TypedDict):
        name: List[str] = ["Hello"]
        value: Union[int, float]
    assert is_json_encodable(TypedDictExample2T, failure_callback=failure_callback)
    class NonTypechekableT:
        name: str
        val: int
    class NonTypecheckableTypedDictExample1T(TypedDict):
        name: List[NonTypechekableT]
        value: Union[int, float]
    assert not is_json_encodable(NonTypecheckableTypedDictExample1T, failure_callback=failure_callback)
    class NonTypecheckableTypedDictExample2T(TypedDict):
        name: str = 10
        value: Union[int, float]
    assert not is_json_encodable(NonTypecheckableTypedDictExample2T, failure_callback=failure_callback)
    class NonEncodableTypedDictExample3T(TypedDict):
        name: bytes
        value: Union[int, float]
    assert not is_json_encodable(NonEncodableTypedDictExample3T, failure_callback=failure_callback)

