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
from typing_json.decoding import from_json_obj, JSON_BASE_TYPES

# (bool, int, float, str, type(None))
NONENCODABLE_BASE_TYPES = tuple(t for t in TYPECHECKABLE_BASE_TYPES if t not in JSON_BASE_TYPES+(Decimal,))

def failure_callback(message: str) -> None:
    print(message)


def test_from_json_obj_typeerrors():
    """ Checks that `from_json_obj` raises `TypeError` on non-typecheckable types or non-json-encodable types.
    """
    class NonTypechekableT:
        name: str
        val: int
        def __init__(self, name, val):
            self.name = name
            self.val = val
    x = NonTypechekableT("x", 0)
    try:
        from_json_obj(x, NonTypechekableT)
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
    (Decimal("1.0"), Decimal, 1),
    (Decimal("1.5"), Decimal, "1.5"),
    (True, Literal[True, 1.5, None], True),
    (1.5, Literal[True, 1.5, None], 1.5),
    (None, Literal[True, 1.5, None], None),
    (True, Union[bool, float, Decimal], True),
    (1.5, Union[bool, float, Decimal], 1.5),
    (Decimal("1.0"), Union[bool, None, Decimal], 1),
    (Decimal("1.5"), Union[bool, None, Decimal], "1.5"),
    (1, int, Decimal(1)),
    (1, int, Decimal("1.0")),
]


def test_from_json_obj_basetypes():
    """ Test `to_json_obj` on JSON base types and `decimal.Decimal`. """
    for val, t, encoding in BASETYPES_ENCODINGS:
        assert from_json_obj(encoding, t) == val

def test_from_json_obj_numbers():
    assert from_json_obj(1.5, Decimal) == Decimal(1.5)
    assert from_json_obj(1, float) == 1.0
    assert from_json_obj(Decimal("1.5"), float) == 1.5
    assert from_json_obj(Decimal("1.0"), float) == 1.0
    try:
        from_json_obj(Decimal("1.5"), float, cast_decimal=False)
        assert False
    except TypeError:
        assert True


from enum import Enum
class EnumT(Enum):
    # pylint:disable=all
    Red = 0
    Green = 1
    Blue = 2


def test_from_json_obj_enums():
    assert from_json_obj("Red", EnumT) == EnumT.Red


def test_from_json_obj_lists():
    """ Checks that lists are decoded correctly. """
    encoding = [1, 2, 3]
    val = from_json_obj(encoding, List[int])
    assert isinstance(val, list)
    assert len(val) == 3
    assert all(val[i] == encoding[i] for i in range(len(encoding)))


def test_from_json_obj_tuples1():
    """ Checks that fixed-length tuples are decoded correctly. """
    encoding = [1, 2, 3]
    val = from_json_obj(encoding, Tuple[int, int, int])
    assert isinstance(val, tuple)
    assert len(val) == 3
    assert all(val[i] == encoding[i] for i in range(len(encoding)))


def test_from_json_obj_tuples2():
    """ Checks that variadic tuples are decoded correctly. """
    encoding = [1, 2, 3]
    val = from_json_obj(encoding, Tuple[int, ...])
    assert isinstance(val, tuple)
    assert len(val) == 3
    assert all(val[i] == encoding[i] for i in range(len(encoding)))


def test_from_json_obj_deque():
    """ Checks that dequeues are decoded correctly. """
    encoding = [1, 2, 3]
    val = from_json_obj(encoding, Deque[int])
    assert isinstance(val, deque)
    assert len(val) == 3
    assert all(val[i] == encoding[i] for i in range(len(encoding)))


def test_from_json_obj_set():
    """ Checks that dequeues are decoded correctly. """
    encoding = [1, 2, 3]
    val = from_json_obj(encoding, Set[int])
    assert isinstance(val, set)
    assert set(val) == set(encoding)


def test_from_json_obj_frozenset():
    """ Checks that dequeues are decoded correctly. """
    encoding = [1, 2, 3]
    val = from_json_obj(encoding, FrozenSet[int])
    assert isinstance(val, frozenset)
    assert set(val) == set(encoding)


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

def test_from_json_obj_dicts():
    """ Checks that dicts are decoded into dicts with the correct key/value pairs. """
    def _assert_eq_dicts(d1, d2):
        assert isinstance(d1, dict)
        assert isinstance(d2, dict)
        assert len(d1) == len(d2)
        assert set(d1.keys()) == set(d2.keys())
        assert all(d1[key] == d2[key] for key in d1)
    for val, t, encoding in DICT_ENCODINGS:
        _assert_eq_dicts(from_json_obj(encoding, t), val)

ORDERED_DICT_ENCODINGS = [
    (OrderedDict([(str(i), i) for i in range(3)]), typing.OrderedDict[str, int], OrderedDict([(str(i), i) for i in range(3)])),
    (OrderedDict([(str(i), i) for i in range(3)]), typing.OrderedDict[Literal["0", "1", "2"], int], OrderedDict([(str(i), i) for i in range(3)])),
    (OrderedDict([(EnumT.Red, 0), (EnumT.Green, 1), (EnumT.Blue, 2)]), typing.OrderedDict[EnumT, int], OrderedDict([("Red", 0), ("Green", 1), ("Blue", 2)])),
    (OrderedDict([(tuple(j for j in range(i)), i) for i in range(3)]), typing.OrderedDict[Tuple[int, ...], int], OrderedDict([(json.dumps([j for j in range(i)]), i) for i in range(3)])),
]


def test_from_json_obj_ordereddicts():
    """ Checks that dicts are decoded into dicts with the correct key/value pairs. """
    def _assert_eq_ordered_dicts(d1, d2):
        assert isinstance(d1, OrderedDict)
        assert isinstance(d2, OrderedDict)
        assert len(d1) == len(d2)
        assert tuple(d1.keys()) == tuple(d2.keys())
        assert all(d1[key] == d2[key] for key in d1)
    for val, t, encoding in ORDERED_DICT_ENCODINGS:
        _assert_eq_ordered_dicts(from_json_obj(encoding, t), val)



class NamedTupleExampleT(NamedTuple):
    name: str
    value: Union[int, float]
    flag: bool = False


def test_is_json_encodable_namedtuple():
    """
        Tests the encoding of namedtuples.
    """
    t = NamedTupleExampleT("t", 1)
    t_encoding = OrderedDict([("name", "t"), ("value", 1)])
    from_json_obj(t_encoding, NamedTupleExampleT) == t


WRONG_TYPE_ENCODINGS = [
    (bool, 1),
    (int, True),
    (float, "hello"),
    (str, 1.5),
    (type(None), 1),
    (None, 1),
    (Decimal, "hi"),
    (EnumT, 1.2),
    (EnumT, "Yellow"),
    (List[int], "hello"),
    (Tuple[int, ...], tuple([1, 2, 3])),
    (Tuple[int, int, int], tuple([1, 2, 3])),
    (Tuple[int, int, int], [1, 2]),
    (Deque[int], deque([1, 2, 3])),
    (Set[int], set([1, 2, 3])),
    (FrozenSet[int], frozenset([1, 2, 3])),
    (Literal[1,2,3], "1.0"),
    (Union[int, float], False),
    (Dict[str, int], [1, 2, 3]),
    (Mapping[str, int], [1, 2, 3]),
    (typing.OrderedDict[str, int], [1, 2, 3]),
    (Dict[str, int], {1: 1, 2: 2, 3: 3}),
    (Mapping[str, int], {1: 1, 2: 2, 3: 3}),
    (typing.OrderedDict[str, int], OrderedDict({1: 1, 2: 2, 3: 3})),
    (NamedTupleExampleT, ("t", 1)),
    (NamedTupleExampleT, OrderedDict([("name", "t"), ("values", [1, 2, 3])])),
    (NamedTupleExampleT, OrderedDict([("name", "t"), ("value", 1), ("blah", None)])),
    (NamedTupleExampleT, OrderedDict([("name", "t")])),
]


def test_from_json_obj_wrong_type():
    """ Test `to_json_obj` on wrong encodings for JSON base types and `decimal.Decimal`. """
    for t, encoding in WRONG_TYPE_ENCODINGS:
        try:
            from_json_obj(encoding, t)
            assert False, "Should not be decoding %s as %s."%(str(encoding), str(t))
        except TypeError:
            assert True