""" Tests for the typing_json.typechecking sub-module. """

from typing import NamedTuple
from collections import namedtuple
from typing_json.typechecking import is_namedtuple

def test_is_namedtuple():
    class A(NamedTuple):
        # pylint:disable=all
        name: str
        value: int
    assert(is_namedtuple(A))
    class B:
        # pylint:disable=all
        name: str
        value: int
    assert(not is_namedtuple(B))
    C = namedtuple("C", ["name", "value"])
    assert(not is_namedtuple(C))
    D = namedtuple("D", ["name", "value"])
    assert(not is_namedtuple(D))
    D._field_types = {"name": str, "value": int}
    assert(is_namedtuple(D))
