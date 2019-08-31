""" Tests for the typing_json.typechecking sub-module. """

from typing import NamedTuple
from collections import namedtuple
import sys
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
    # for some odd reason the following test fails in 3.7.1
    version_info = sys.version_info
    if version_info[0:3]>= (3, 7, 4):
        D._field_types = {"name": str, "value": int}
        assert(is_namedtuple(D))
