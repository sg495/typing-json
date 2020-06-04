""" Tests for `typing_json.typechecking.to_json_obj` """
# pylint: disable = line-too-long, invalid-name, missing-docstring

# standard imports
import json
import typing
from typing import Union, Optional, List, Tuple, Set, FrozenSet, Mapping, Dict, NamedTuple, Deque
from decimal import Decimal
from collections import deque, OrderedDict

# external dependencies
from typing_extensions import Literal

# internal imports
from typing_json.typechecking import TYPECHECKABLE_BASE_TYPES
from typing_json.encoding import to_json_obj, JSON_BASE_TYPES

# (bool, int, float, str, type(None))
NONENCODABLE_BASE_TYPES = tuple(t for t in TYPECHECKABLE_BASE_TYPES if t not in JSON_BASE_TYPES+(Decimal,))

def failure_callback(message: str) -> None:
    print(message)


def test_to_json_obj_typeerrors():
    """ Checks that `to_json_obj` raises `TypeError` on non-typecheckable types and when `obj` is not an instance of `t`.
    """
    class NonTypechekableT:
        name: str
        val: int
        def __init__(self, name, val):
            self.name = name
            self.val = val
    x = NonTypechekableT("x", 0)
    try:
        to_json_obj(x, NonTypechekableT)
        assert False
    except TypeError:
        assert True
    try:
        to_json_obj(0, str)
        assert False
    except TypeError:
        assert True


BASETYPES_ENCODINGS = [
    (True, bool, True),
    (1, int, 1),
    (1.5, float, 1.5),
    ("hello", str, "hello"),
    (None, type(None), None),
    (None, None, None),
    (Decimal("1.0"), Decimal, "1.0"),
    (Decimal("1.5"), Decimal, "1.5"),
    (True, Literal[True, 1.5, None], True),
    (1.5, Literal[True, 1.5, None], 1.5),
    (None, Literal[True, 1.5, None], None),
    (True, Union[bool, float, Decimal], True),
    (1.5, Union[bool, float, Decimal], 1.5),
    (Decimal("1.0"), Union[bool, str, Decimal], "1.0"),
    (Decimal("1.5"), Union[bool, str, Decimal], "1.5"),
]


def test_to_json_obj_basetypes():
    """ Test `to_json_obj` on JSON base types and `decimal.Decimal`. """
    for val, t, encoding in BASETYPES_ENCODINGS:
        assert to_json_obj(val, t) == encoding
    assert to_json_obj(Decimal("1.5"), Decimal, use_decimal=True) == Decimal("1.5")


from enum import Enum
class EnumT(Enum):
    # pylint:disable=all
    Red = 0
    Green = 1
    Blue = 2

def test_to_json_obj_enums():
    assert to_json_obj(EnumT.Red, EnumT) == "Red"


SEQUENCES_ENCODINGS = [
    ([0, 1, 2], List[int], [0, 1, 2]),
    ((0, 1, 2), Tuple[int, ...], [0, 1, 2]),
    ((0, 1, 2), Tuple[int, int, int], [0, 1, 2]),
    (deque([0, 1, 2]), Deque[int], [0, 1, 2]),
]


def test_to_json_obj_sequences():
    """ Checks that sequences are encoded into lists with the correct elements. """
    def _assert_eq_lists(l1, l2):
        assert isinstance(l1, list)
        assert isinstance(l2, list)
        assert len(l1) == len(l2)
        assert all(l1[i] == l2[i] for i in range(len(l1)))
        assert all(type(l1[i]) == type(l2[i]) for i in range(len(l1)))
    for val, t, encoding in SEQUENCES_ENCODINGS:
        _assert_eq_lists(to_json_obj(val, t), encoding)


SETS_ENCODINGS = [
    ({0, 1, 2}, Set[int], [0, 1, 2]),
    (frozenset({0, 1, 2}), FrozenSet[int], [0, 1, 2]),
]


def test_to_json_obj_sets():
    """ Checks that sets are encoded into lists with the correct elements. """
    for val, t, encoding in SETS_ENCODINGS:
        to_json_obj(val, t) == encoding


DICT_ENCODINGS = [
    ({str(i): i for i in range(3)}, Dict[str, int], {str(i): i for i in range(3)}),
    ({str(i): i for i in range(3)}, Mapping[str, int], {str(i): i for i in range(3)}),
    ({str(i): i for i in range(3)}, Dict[Literal["0", "1", "2"], int], {str(i): i for i in range(3)}),
    ({str(i): i for i in range(3)}, Mapping[Literal["0", "1", "2"], int], {str(i): i for i in range(3)}),
    ({EnumT.Red: 0, EnumT.Green: 1, EnumT.Blue: 2}, Dict[EnumT, int], {"Red": 0, "Green": 1, "Blue": 2}),
    ({EnumT.Red: 0, EnumT.Green: 1, EnumT.Blue: 2}, Mapping[EnumT, int], {"Red": 0, "Green": 1, "Blue": 2}),
    ({tuple(j for j in range(i)): i for i in range(3)}, Dict[Tuple[int, ...], int], {json.dumps([j for j in range(i)]): i for i in range(3)}),
    ({tuple(j for j in range(i)): i for i in range(3)}, Mapping[Tuple[int, ...], int], {json.dumps([j for j in range(i)]): i for i in range(3)}),
]


def test_to_json_obj_dicts():
    """ Checks that dicts/mappings are encoded into dicts with the correct key/value pairs. """
    for val, t, encoding in DICT_ENCODINGS:
        to_json_obj(val, t) == encoding


ORDERED_DICT_ENCODINGS = [
    (OrderedDict([(str(i), i) for i in range(3)]), typing.OrderedDict[str, int], OrderedDict([(str(i), i) for i in range(3)])),
    (OrderedDict([(str(i), i) for i in range(3)]), typing.OrderedDict[Literal["0", "1", "2"], int], OrderedDict([(str(i), i) for i in range(3)])),
    (OrderedDict([(EnumT.Red, 0), (EnumT.Green, 1), (EnumT.Blue, 2)]), typing.OrderedDict[EnumT, int], OrderedDict([("Red", 0), ("Green", 1), ("Blue", 2)])),
    (OrderedDict([(tuple(j for j in range(i)), i) for i in range(3)]), typing.OrderedDict[Tuple[int, ...], int], OrderedDict([(json.dumps([j for j in range(i)]), i) for i in range(3)])),
]


def test_to_json_obj_ordereddicts():
    """ Checks that dicts/mappings are encoded into dicts with the correct key/value pairs. """
    for val, t, encoding in ORDERED_DICT_ENCODINGS:
        assert to_json_obj(val, t) == encoding


def test_is_json_encodable_namedtuple():
    """
        Tests the encoding of namedtuples.
    """
    class NamedTupleExampleT(NamedTuple):
        name: str
        value: Union[int, float]
    t = NamedTupleExampleT("t", 1)
    t_encoding = OrderedDict([("name", "t"), ("value", 1)])
    assert to_json_obj(t, NamedTupleExampleT) == t_encoding

def test_to_json_obj_large_collections_int():
    large_list: List[int] = []
    for i in range(1000):
        large_list.append(i)
    assert to_json_obj(large_list, List[int]) == large_list


def test_to_json_obj_large_collections_decimal():
    large_list: List[Decimal] = []
    for i in range(1000):
        large_list.append(Decimal(i))
    assert to_json_obj(large_list, List[Decimal], use_decimal=True) == large_list
    assert to_json_obj(large_list, List[Decimal], use_decimal=False) == [str(el) for el in large_list]

def test_to_json_obj_large_collections_none():
    large_list: List[None] = []
    for i in range(1000):
        large_list.append(None)
    assert to_json_obj(large_list, List[None]) == large_list
    assert to_json_obj(large_list, List[type(None)]) == large_list

def test_to_json_obj_large_collections_enum():
    large_list: List[EnumT] = []
    for i in range(1000):
        large_list.append(EnumT.Red)
    assert to_json_obj(large_list, List[EnumT]) == ["Red" for _ in large_list]


def test_to_json_obj_large_collections_other():
    large_list: List[Tuple[int, int]] = []
    for i in range(1000):
        large_list.append((i, i+1))
    assert to_json_obj(large_list, List[Tuple[int, int]]) == [list(el) for el in large_list]


def test_to_json_obj_large_collections_namedtuple():
    class Pair(NamedTuple):
        left: int
        right: int
    large_list: List[Pair] = []
    large_list_encoding_lists: List[list] = []
    large_list_encoding_dicts: List[dict] = []
    for i in range(1000):
        large_list.append(Pair(i, i+1))
        large_list_encoding_lists.append([i, i+1])
        large_list_encoding_dicts.append({"left": i, "right": i+1})
    assert to_json_obj(large_list, List[Pair], namedtuples_as_lists=True) == large_list_encoding_lists
    assert to_json_obj(large_list, List[Pair], namedtuples_as_lists=False) == large_list_encoding_dicts

