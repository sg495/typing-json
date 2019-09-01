""" Tests for the typing_json.encoding sub-module. """

import typing
from typing import NamedTuple, List, Dict, Any, Union, Set, Tuple, FrozenSet
import collections
from typing_extensions import Literal

from typing_json.encoding import is_json_encodable, to_json_obj, JSON_BASE_TYPES
from .test_typechecking import make_generic_collection_types

BASE_TYPES: Dict[Any, Any] = {
    bool: True, # bool inherits from int, see https://www.python.org/dev/peps/pep-0285/
    int: 1,
    float: 1.0,
    str: "hello",
    type(None): None,
    ...: ...,
}

BASE_TYPES_INHERITANCE: Dict[Any, List[Any]] = {
    bool: [int]
}

def contains_non_json_encodable_dict(t: Any) -> bool:
    # pylint:disable=missing-docstring,invalid-name,line-too-long
    if hasattr(t, "__origin__") and t.__origin__ in (dict, collections.OrderedDict) and t.__args__[0] != str:
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        return any(contains_non_json_encodable_dict(s) for s in t.__args__)
    return False

def test_is_json_encodable():
    # pylint:disable=line-too-long,missing-docstring,invalid-name
    for t in JSON_BASE_TYPES:
        assert is_json_encodable(t)
    assert is_json_encodable(None)
    assert is_json_encodable(...)
    class A(NamedTuple):
        name: str
        value: int
    assert is_json_encodable(A)
    class B:
        # pylint:disable=too-few-public-methods
        name: str
        value: int
    assert not is_json_encodable(B)
    type_dict, inherit_dict = make_generic_collection_types(BASE_TYPES, BASE_TYPES_INHERITANCE)
    type_dict, inherit_dict = make_generic_collection_types(type_dict, inherit_dict)
    for t in type_dict:
        if contains_non_json_encodable_dict(t):
            continue
        assert is_json_encodable(t)
    type_dict, inherit_dict = make_generic_collection_types(BASE_TYPES, BASE_TYPES_INHERITANCE)
    for t in type_dict:
        if t is ... or contains_non_json_encodable_dict(t):
            continue
        for s in type_dict:
            if s is ... or contains_non_json_encodable_dict(s):
                continue
            assert is_json_encodable(Union[t, s])
    assert is_json_encodable(Literal["s", 0, 2, False, None])
    assert not is_json_encodable(Literal["s", []]) # type:ignore
    assert not is_json_encodable(1.0+1.0j)

def test_to_json_obj():
    # pylint:disable=missing-docstring,invalid-name
    try:
        to_json_obj(1.0j, complex)
        assert False
    except ValueError:
        assert True
    try:
        to_json_obj("hi", int)
        assert False
    except ValueError:
        assert True
    for t in BASE_TYPES:
        obj = BASE_TYPES[t]
        if t is ...:
            assert to_json_obj(obj, t) is None
        else:
            assert to_json_obj(obj, t) is obj
    class A(NamedTuple):
        name: str
        value: int
    a = A("hi", 0)
    assert to_json_obj(a, A) == {"name": "hi", "value": 0}
    assert to_json_obj(1, Union[int, float]) == 1
    assert to_json_obj(1.0, Union[int, float]) == 1.0
    assert to_json_obj("hi", Literal["hi", 1]) == "hi"
    assert to_json_obj(1, Literal["hi", 1]) == 1
    assert to_json_obj(["hi", "my"], List[str]) == ["hi", "my"]
    set_example = to_json_obj(set(["hi", "my"]), Set[str])
    assert isinstance(set_example, list)
    assert set(set_example) == set(["hi", "my"])
    frozenset_example = to_json_obj(frozenset(["hi", "my"]), FrozenSet[str])
    assert isinstance(frozenset_example, list)
    assert frozenset(frozenset_example) == frozenset(["hi", "my"])
    assert to_json_obj(tuple(["hi", "my"]), Tuple[str, ...]) == ["hi", "my"]
    assert to_json_obj(tuple(["hi", 0]), Tuple[str, int]) == ["hi", 0]
    d = {"name": "hi", "value": "zero"}
    assert to_json_obj(d, Dict[str, str]) == d
    od = collections.OrderedDict()
    od["value"] = "zero"
    od["name"] = "hi"
    assert to_json_obj(od, typing.OrderedDict[str, str]) == od
