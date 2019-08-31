""" Tests for the typing_json.typechecking sub-module. """

import typing
from typing import NamedTuple, List, Tuple, Set, FrozenSet, Dict, Union, Any, Deque, Optional
from typing_extensions import Literal
import collections
from collections import namedtuple, deque, ChainMap, Counter, UserDict, UserList, UserString
import sys
from typing_json.typechecking import is_typecheckable, is_instance, is_namedtuple

BASE_TYPES: Dict[Any, Any] = {
    bool: True, # bool inherits from int, see https://www.python.org/dev/peps/pep-0285/
    int: 1,
    float: 1.0,
    complex: 1.0j,
    str: "hello",
    bytes: b"hello",
    bytearray: bytearray(b"hello"),
    memoryview: memoryview(b"hello"),
    list: ["hello", 0],
    tuple: ("hello", 0),
    range: range(0, 15),
    slice: slice(15),
    set: set(["hello", 0]),
    frozenset: frozenset(["hello", 0]),
    dict: {"str": "hello", "int": 0},
    type: str,
    None: None,
    ...: ...,
    NotImplemented : NotImplemented,
}

BASE_TYPES_INHERITANCE: Dict[Any, List[Any]] = {
    bool: [int]
}

COLLECTION_TYPES: Dict[Any, Any] = {
    deque: deque(["hello", 0]),
    collections.OrderedDict: collections.OrderedDict({"str": "hello", "int": 0}),
}

COLLECTION_TYPES_INHERITANCE: Dict[Any, List[Any]] = {
    collections.OrderedDict: [dict],
}

def _make_generic_collection_types(level: int):
    if level <= 0:
        type_dict = {**BASE_TYPES, **COLLECTION_TYPES}
        inherit_dict = {**BASE_TYPES_INHERITANCE, **COLLECTION_TYPES_INHERITANCE}
        return (type_dict, inherit_dict)
    rec_type_dict, rec_inherit_dict = _make_generic_collection_types(level-1)
    type_dict = {}
    inherit_dict = {}
    for t in rec_type_dict:
        if t in (Ellipsis, NotImplemented):
            continue
        # lists
        type_dict[List[t]] = list([rec_type_dict[t], rec_type_dict[t]]) # type:ignore
        inherit_dict[List[t]] = [list] # type:ignore
        if t in rec_inherit_dict:
            inherit_dict[List[t]] += [List[s] for s in rec_inherit_dict[t]] # type:ignore
        ## variadic tuples
        type_dict[Tuple[t, ...]] = tuple([rec_type_dict[t], rec_type_dict[t]]) # type:ignore
        inherit_dict[Tuple[t,...]] = [tuple, Tuple[t, t]] # type:ignore
        if t in rec_inherit_dict:
            inherit_dict[Tuple[t,...]] += [Tuple[s,...] for s in rec_inherit_dict[t]] # type:ignore
            inherit_dict[Tuple[t,...]] += [Tuple[s, s] for s in rec_inherit_dict[t]] # type:ignore
        ## 1-tuples
        type_dict[Tuple[t]] = tuple([rec_type_dict[t]]) # type:ignore
        inherit_dict[Tuple[t]] = [tuple, Tuple[t,...]] # type:ignore
        if t in rec_inherit_dict:
            inherit_dict[Tuple[t]] += [Tuple[s] for s in rec_inherit_dict[t]] # type:ignore
            inherit_dict[Tuple[t]] += [Tuple[s,...] for s in rec_inherit_dict[t]] # type:ignore
        ## 2-tuples
        type_dict[Tuple[t, t]] = tuple([rec_type_dict[t], rec_type_dict[t]]) # type:ignore
        inherit_dict[Tuple[t, t]] = [tuple, Tuple[t,...]] # type:ignore
        if t in rec_inherit_dict:
            inherit_dict[Tuple[t, t]] += [Tuple[s, s] for s in rec_inherit_dict[t]] # type:ignore
            inherit_dict[Tuple[t, t]] += [Tuple[s,...] for s in rec_inherit_dict[t]] # type:ignore
        ## 3-tuples
        type_dict[Tuple[t, t, t]] = tuple([rec_type_dict[t], rec_type_dict[t], rec_type_dict[t]]) # type:ignore
        inherit_dict[Tuple[t, t, t]] = [tuple, Tuple[t,...]] # type:ignore
        if t in rec_inherit_dict:
            inherit_dict[Tuple[t, t, t]] += [Tuple[s, s, s] for s in rec_inherit_dict[t]] # type:ignore
            inherit_dict[Tuple[t, t, t]] += [Tuple[s,...] for s in rec_inherit_dict[t]] # type:ignore
        # deque
        type_dict[Deque[t]] = deque([rec_type_dict[t], rec_type_dict[t]]) # type:ignore
        inherit_dict[Deque[t]] = [deque] # type:ignore
        if t in rec_inherit_dict:
            inherit_dict[Deque[t]] += [Deque[s] for s in rec_inherit_dict[t]] # type:ignore
        try:
            hash(rec_type_dict[t])
            # sets
            type_dict[Set[t]] = set([rec_type_dict[t], rec_type_dict[t]]) # type:ignore
            inherit_dict[Set[t]] = [set] # type:ignore
            if t in rec_inherit_dict:
                inherit_dict[Set[t]] += [Set[s] for s in rec_inherit_dict[t]] # type:ignore
            # frozensets
            type_dict[FrozenSet[t]] = frozenset([rec_type_dict[t], rec_type_dict[t]]) # type:ignore
            inherit_dict[FrozenSet[t]] = [frozenset] # type:ignore
            if t in rec_inherit_dict:
                inherit_dict[FrozenSet[t]] += [FrozenSet[s] for s in rec_inherit_dict[t]] # type:ignore
            for s in rec_type_dict:
                # dicts
                type_dict[Dict[t, s]] = dict({rec_type_dict[t]: rec_type_dict[s]}) # type:ignore
                inherit_dict[Dict[t, s]] = [dict] # type:ignore
                if t in rec_inherit_dict and s in rec_inherit_dict:
                    inherit_dict[Dict[t, s]] += [Dict[a, b] for a in rec_inherit_dict[t] for b in rec_inherit_dict[s]] # type:ignore
                if t in rec_inherit_dict:
                    inherit_dict[Dict[t, s]] += [Dict[a, s] for a in rec_inherit_dict[t]] # type:ignore
                if s in rec_inherit_dict:
                    inherit_dict[Dict[t, s]] += [Dict[t, b] for b in rec_inherit_dict[s]] # type:ignore
                # OrderedDicts
                type_dict[typing.OrderedDict[t, s]] = collections.OrderedDict({rec_type_dict[t]: rec_type_dict[s]}) # type:ignore
                inherit_dict[typing.OrderedDict[t, s]] = [collections.OrderedDict, dict, Dict[t, s]] # type:ignore
                if t in rec_inherit_dict and s in rec_inherit_dict:
                    inherit_dict[typing.OrderedDict[t, s]] += [typing.OrderedDict[a, b] for a in rec_inherit_dict[t] for b in rec_inherit_dict[s]] # type:ignore
                    inherit_dict[typing.OrderedDict[t, s]] += [Dict[a, b] for a in rec_inherit_dict[t] for b in rec_inherit_dict[s]] # type:ignore
                if t in rec_inherit_dict:
                    inherit_dict[typing.OrderedDict[t, s]] += [typing.OrderedDict[a, s] for a in rec_inherit_dict[t]] # type:ignore
                    inherit_dict[typing.OrderedDict[t, s]] += [Dict[a, s] for a in rec_inherit_dict[t]] # type:ignore
                if s in rec_inherit_dict:
                    inherit_dict[typing.OrderedDict[t, s]] += [typing.OrderedDict[t, b] for b in rec_inherit_dict[s]] # type:ignore
                    inherit_dict[typing.OrderedDict[t, s]] += [Dict[t, b] for b in rec_inherit_dict[s]] # type:ignore
        except TypeError:
            ... # do nothing, this just means t was not hashable
    return (type_dict, inherit_dict)

def _test_types(type_dict, inherit_dict):
    for t in type_dict:
        for s in type_dict:
            if t == s:
                assert(is_instance(type_dict[s], t))
            elif s in inherit_dict and t in inherit_dict[s]:
                assert(is_instance(type_dict[s], t))
            else:
                assert(not is_instance(type_dict[s], t))
    for t in type_dict:
        assert(is_instance(type_dict[t], object))

def test_is_instance_base_types():
    type_dict = {**BASE_TYPES, **COLLECTION_TYPES}
    inherit_dict = {**BASE_TYPES_INHERITANCE, **COLLECTION_TYPES_INHERITANCE}
    _test_types(type_dict, inherit_dict)

def test_is_instance_generic_collection_types():
    type_dict = {}
    inherit_dict = {}
    for i in range(0, 2):
        type_dict_i, inherit_dict_i = _make_generic_collection_types(i)
        type_dict.update(type_dict_i)
        inherit_dict.update(inherit_dict_i)
    _test_types(type_dict, inherit_dict)

def test_is_instance_optional():
    type_dict = {**BASE_TYPES, **COLLECTION_TYPES}
    for t in type_dict:
        if t in (Ellipsis, NotImplemented):
            continue
        assert(is_instance(None, Optional[t]))
        assert(is_instance(type_dict[t], Optional[t]))

def test_is_instance_union():
    type_dict = {**BASE_TYPES, **COLLECTION_TYPES}
    for t in type_dict:
        if t in (Ellipsis, NotImplemented):
            continue
        for s in type_dict:
            if s in (Ellipsis, NotImplemented):
                continue
            assert(is_instance(type_dict[t], Union[t, s]))
            assert(is_instance(type_dict[s], Union[t, s]))
    for t in type_dict:
        if t in (Ellipsis, NotImplemented):
            continue
        for s in type_dict:
            if s in (Ellipsis, NotImplemented):
                continue
            for u in type_dict:
                if u in (Ellipsis, NotImplemented):
                    continue
                assert(is_instance(type_dict[t], Union[t, s, u]))
                assert(is_instance(type_dict[s], Union[t, s, u]))
                assert(is_instance(type_dict[u], Union[t, s, u]))

def test_is_instance_literal():
    type_dict = {**BASE_TYPES, **COLLECTION_TYPES}
    for t in type_dict:
        for s in type_dict:
            assert(is_instance(type_dict[t], Literal[type_dict[t], type_dict[s]]))
            assert(is_instance(type_dict[s], Literal[type_dict[t], type_dict[s]]))
    for t in type_dict:
        for s in type_dict:
            for u in type_dict:
                assert(is_instance(type_dict[t], Literal[type_dict[t], type_dict[s], type_dict[u]]))
                assert(is_instance(type_dict[s], Literal[type_dict[t], type_dict[s], type_dict[u]]))
                assert(is_instance(type_dict[u], Literal[type_dict[t], type_dict[s], type_dict[u]]))

def test_is_typecheckable_namedtuple():
    class A(NamedTuple):
        # pylint:disable=all
        name: List[str]
        value: Union[int, float]
    assert(is_typecheckable(A))
    class B:
        # pylint:disable=all
        name: List[str]
        value: Union[int, float]
    assert(not is_typecheckable(B))

def test_is_namedtuple():
    class A(NamedTuple):
        # pylint:disable=all
        name: List[str]
        value: Union[int, float]
    assert(is_namedtuple(A))
    class B:
        # pylint:disable=all
        name: List[str]
        value: Union[int, float]
    assert(not is_namedtuple(B))
    C = namedtuple("C", ["name", "value"])
    assert(not is_namedtuple(C))
    D = namedtuple("D", ["name", "value"])
    assert(not is_namedtuple(D))
    # for some odd reason the following test fails in 3.7.1
    version_info = sys.version_info
    if version_info[0:3]>= (3, 7, 4):
        D._field_types = {"name": str, "value": int}
        assert(is_namedtuple(D))
