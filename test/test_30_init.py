# pylint: disable = line-too-long, invalid-name, missing-docstring
""" Tests for `typing_json.dump`, `typing_json.dumps`, `typing_json.load` and `typing_json.loads`. """

# standard imports
import io
from decimal import Decimal
from typing import Union

# external dependencies
from typing_extensions import Literal

# internal imports
from typing_json import dump, dumps, load, loads


BASETYPES_VALUES = [
    (True, bool),
    (1, int),
    (1.5, float),
    ("hello", str),
    (None, type(None)),
    (None, None),
    (True, Literal[True, 1.5, None]),
    (1.5, Literal[True, 1.5, None]),
    (None, Literal[True, 1.5, None]),
    (True, Union[bool, float, Decimal]),
    (1.5, Union[bool, float, Decimal]),
]


def test_basetypes():
    for val, t in BASETYPES_VALUES:
        assert val == loads(dumps(val, t), t)
        with io.StringIO() as f:
            dump(val, t, f)
            data = f.getvalue()
        with io.StringIO(data) as f:
            assert load(f, t) == val

def test_error():
    try:
        with io.StringIO() as f:
            dump(b"hello", bytes, f)
        assert False
    except TypeError:
        assert True
    try:
        dumps(b"hello", bytes)
        assert False
    except TypeError:
        assert True
    try:
        with io.StringIO() as f:
            load(f, bytes)
        assert False
    except TypeError:
        assert True
    try:
        loads("hello", bytes)
        assert False
    except TypeError:
        assert True
