""" Tests for the typing_json.encoding sub-module. """

import typing
from typing import NamedTuple, List, Dict, Any, Union, Set, Tuple, FrozenSet, Deque
import collections
from collections import deque
from typing_extensions import Literal

from typing_json.encoding import to_json_obj
from typing_json.decoding import from_json_obj
from .test_0_typechecking import make_generic_collection_types

BASE_TYPES: Dict[Any, Any] = {
    bool: True, # bool inherits from int, see https://www.python.org/dev/peps/pep-0285/
    int: 1,
    float: 1.0,
    str: "hello",
    type(None): None,
}

BASE_TYPES_INHERITANCE: Dict[Any, List[Any]] = {
    bool: [int]
}

# def contains_non_json_encodable_dict(t: Any) -> bool:
#     # pylint:disable=missing-docstring,invalid-name,line-too-long
#     if hasattr(t, "__origin__") and t.__origin__ in (dict, collections.OrderedDict) and t.__args__[0] != str:
#         return True
#     if hasattr(t, "__origin__") and hasattr(t, "__args__"):
#         return any(contains_non_json_encodable_dict(s) for s in t.__args__)
#     return False

def test_from_json_obj():
    # pylint:disable=missing-docstring,invalid-name
    for t in BASE_TYPES:
        obj = BASE_TYPES[t]
        if t is ...:
            assert from_json_obj(to_json_obj(obj, t), t) is ...
        else:
            assert from_json_obj(to_json_obj(obj, t), t) is obj
    assert from_json_obj(to_json_obj(None, None), None) is None
    class A(NamedTuple):
        name: str
        value: int
    a = A("hi", 0)
    # pylint:disable=line-too-long
    assert from_json_obj(to_json_obj(a, A), A) == a
    assert from_json_obj(["hi", 0], A) == a
    a._field_defaults["value"] = 0 # type:ignore #pylint:disable=no-member,protected-access
    assert from_json_obj({"name": "hi"}, A) == a
    assert from_json_obj(to_json_obj(1, Union[int, float]), Union[int, float]) == 1
    assert from_json_obj(to_json_obj(1.0, Union[int, float]), Union[int, float]) == 1.0
    assert from_json_obj(to_json_obj("hi", Literal["hi", 1]), Literal["hi", 1]) == "hi"
    assert from_json_obj(to_json_obj(1, Literal["hi", 1]), Literal["hi", 1]) == 1
    assert from_json_obj(to_json_obj(["hi", "my"], List[str]), List[str]) == ["hi", "my"]
    assert from_json_obj(to_json_obj(set(["hi", "my"]), Set[str]), Set[str]) == set(["hi", "my"])
    assert from_json_obj(to_json_obj(deque(["hi", "my"]), Deque[str]), Deque[str]) == deque(["hi", "my"])
    assert from_json_obj(to_json_obj(frozenset(["hi", "my"]), FrozenSet[str]), FrozenSet[str]) == frozenset(["hi", "my"])
    assert from_json_obj(to_json_obj(tuple(["hi", "my"]), Tuple[str, ...]), Tuple[str, ...]) == tuple(["hi", "my"])
    assert from_json_obj(to_json_obj(tuple(["hi", 0]), Tuple[str, int]), Tuple[str, int]) == tuple(["hi", 0])
    d = {"name": "hi", "value": "zero"}
    assert from_json_obj(to_json_obj(d, Dict[str, str]), Dict[str, str]) == d
    od = collections.OrderedDict(d)
    assert from_json_obj(to_json_obj(od, typing.OrderedDict[str, str]), typing.OrderedDict[str, str]) == od
    d = {frozenset(["hi", "my"]): "hi", frozenset(["value", "money"]): "zero"}
    assert from_json_obj(to_json_obj(d, Dict[FrozenSet[str], str]), Dict[FrozenSet[str], str]) == d
    od = collections.OrderedDict(d)
    assert from_json_obj(to_json_obj(od, typing.OrderedDict[FrozenSet[str], str]), typing.OrderedDict[FrozenSet[str], str]) == od

def test_from_json_obj_literal():
    # pylint:disable=missing-docstring,invalid-name
    d = {
        "hi": 0,
        "bye": 1
    }
    t = Dict[Literal["hi", "bye"], int]
    assert from_json_obj(to_json_obj(d, t), t) == d
    d = {
        0: 0,
        1: 1
    }
    t = Dict[Literal[0, 1], int]
    assert from_json_obj(to_json_obj(d, t), t) == d
    d = {
        "hi": 0,
        1.2: 1
    }
    t = Dict[Literal["hi", 1.2], int]
    assert from_json_obj(to_json_obj(d, t), t) == d
    d = {
        "hi": 0,
        None: 1
    }
    t = Dict[Literal["hi", None], int]
    assert from_json_obj(to_json_obj(d, t), t) == d
    d = {
        True: 0,
        1.2: 1
    }
    t = Dict[Literal[True, 1.2], int]
    assert from_json_obj(to_json_obj(d, t), t) == d

def test_from_json_obj_errors():
    # pylint:disable=too-many-branches, too-many-statements
    try:
        from_json_obj(1.0j, complex)
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", int)
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj(1.0, None)
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj(1.0, type(None))
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj(1.0, ...)
        assert False
    except TypeError:
        assert True
    class A(NamedTuple):
        name: str
        value: int
    try:
        from_json_obj(1.0, A)
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj([1.0], A)
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj({"name": "hi"}, A)
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj({"name": "hi", "value": 0, "extra": None}, A)
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", Union[int, float, bool])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", List[str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", Deque[str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", Set[str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", FrozenSet[str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", Tuple[str, ...])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", Tuple[str, int])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", Literal[0, 1])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj(["hi"], Tuple[str, int])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", Dict[str, str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj({0: "hi"}, Dict[str, str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj("hi", typing.OrderedDict[str, str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj(collections.OrderedDict({0: "hi"}), typing.OrderedDict[str, str])
        assert False
    except TypeError:
        assert True
    try:
        from_json_obj({"name": "hi"}, typing.OrderedDict[str, str])
        assert False
    except TypeError:
        assert True
