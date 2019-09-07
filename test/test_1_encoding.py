""" Tests for the typing_json.encoding sub-module. """

import typing
from typing import NamedTuple, List, Dict, Any, Union, Set, Tuple, FrozenSet, Mapping
import collections
import io
from typing_extensions import Literal

from typing_json import dump, dumps, load, loads
from typing_json.typechecking import is_hashable
from typing_json.encoding import is_json_encodable, to_json_obj, JSON_BASE_TYPES
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

def contains_non_json_encodable_dict(t: Any) -> bool:
    # pylint:disable=missing-docstring,invalid-name,line-too-long
    if hasattr(t, "__origin__") and t.__origin__ in (dict, collections.OrderedDict, collections.abc.Mapping) and not is_hashable(t.__args__[0]):
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        return any(contains_non_json_encodable_dict(s) for s in t.__args__)
    return False


def test_dump_load():
    # pylint:disable=missing-docstring,invalid-name
    for t in BASE_TYPES:
        obj = BASE_TYPES[t]
        assert loads(dumps(obj, t), t) == obj
        data = ""
        with io.StringIO() as f:
            dump(obj, t, f)
            data = f.getvalue()
        with io.StringIO(data) as f:
            assert load(f, t) == obj
    class B:
        # pylint:disable=too-few-public-methods
        name: str
        value: int
    assert not is_json_encodable(B)
    try:
        dump(None, B, None)
        assert False
    except TypeError:
        assert True
    try:
        dumps(None, B)
        assert False
    except TypeError:
        assert True
    try:
        load(None, B)
        assert False
    except TypeError:
        assert True
    try:
        loads("", B)
        assert False
    except TypeError:
        assert True


def test_is_json_encodable_union():
    # pylint:disable=line-too-long,missing-docstring,invalid-name
    type_dict, _ = make_generic_collection_types(BASE_TYPES, BASE_TYPES_INHERITANCE)
    for t in type_dict:
        if contains_non_json_encodable_dict(t):
            assert not is_json_encodable(t)
            continue
        for s in type_dict:
            if contains_non_json_encodable_dict(s):
                assert not is_json_encodable(s)
                continue
            assert is_json_encodable(Union[t, s])

def test_is_json_encodable_misc():
    # pylint:disable=line-too-long,missing-docstring,invalid-name
    assert is_json_encodable(Literal["s", 0, 2, False, None])
    assert not is_json_encodable(Literal["s", []]) # type:ignore
    assert not is_json_encodable(1.0+1.0j)
    assert is_json_encodable(None)
    assert not is_json_encodable(...)
    class A(NamedTuple):
        name: str
        value: int
    assert is_json_encodable(A)
    class B:
        # pylint:disable=too-few-public-methods
        name: str
        value: int
    assert not is_json_encodable(B)

def test_is_json_encodable_collections():
    # pylint:disable=line-too-long,missing-docstring,invalid-name
    for t in JSON_BASE_TYPES:
        assert is_json_encodable(t)
    type_dict, inherit_dict = make_generic_collection_types(BASE_TYPES, BASE_TYPES_INHERITANCE)
    type_dict, inherit_dict = make_generic_collection_types(type_dict, inherit_dict)
    for t in type_dict:
        assert is_json_encodable(t) == (not contains_non_json_encodable_dict(t))
        for s in BASE_TYPES:
            for q in (Dict, typing.OrderedDict, Mapping):
                r = q[t, s]
                assert is_json_encodable(r) == (not contains_non_json_encodable_dict(r))


def test_to_json_obj():
    # pylint:disable=missing-docstring,invalid-name
    try:
        to_json_obj(1.0j, complex)
        assert False
    except TypeError:
        assert True
    try:
        to_json_obj("hi", int)
        assert False
    except TypeError:
        assert True
    for t in BASE_TYPES:
        obj = BASE_TYPES[t]
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
    d = {frozenset(["hi", "my"]): "hi", frozenset(["value", "money"]): "zero"}
    ds1 = {"[\"hi\", \"my\"]": "hi", "[\"value\", \"money\"]": "zero"}
    ds2 = {"[\"my\", \"hi\"]": "hi", "[\"value\", \"money\"]": "zero"}
    ds3 = {"[\"hi\", \"my\"]": "hi", "[\"money\", \"value\"]": "zero"}
    ds4 = {"[\"my\", \"hi\"]": "hi", "[\"money\", \"value\"]": "zero"}
    assert any(to_json_obj(d, Dict[FrozenSet[str], str]) == ds for ds in [ds1, ds2, ds3, ds4])
    od = collections.OrderedDict(d)
    ods1 = collections.OrderedDict(ds1)
    ods2 = collections.OrderedDict(ds2)
    ods3 = collections.OrderedDict(ds3)
    ods4 = collections.OrderedDict(ds4)
    assert any(to_json_obj(od, typing.OrderedDict[FrozenSet[str], str]) == ods for ods in [ods1, ods2, ods3, ods4])

def test_failure_callbacks():
    # pylint:disable=missing-docstring,invalid-name
    trace = []
    def failure_callback(message: str):
        trace.append(message)
    class A(NamedTuple):
        name: str
        b: bytes
    class B:
        #pylint:disable=all
        name: str
        value: int
    assert not is_json_encodable(A, failure_callback)
    assert not is_json_encodable(List[bytes], failure_callback)
    assert not is_json_encodable(Tuple[bytes, ...], failure_callback)
    assert not is_json_encodable(Tuple[int, A, str], failure_callback)
    assert not is_json_encodable(Union[int, A, str], failure_callback)
    assert not is_json_encodable(Dict[A, str], failure_callback)
    assert not is_json_encodable(Dict[bytes, str], failure_callback)
    assert not is_json_encodable(Dict[B, str], failure_callback)
    assert not is_json_encodable(Dict[List[int], str], failure_callback)
    assert not is_json_encodable(Dict[str, A], failure_callback)
    assert not is_json_encodable(Literal[b"hi", "bye"], failure_callback)
