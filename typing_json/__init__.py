# pylint:disable = line-too-long, invalid-name,
"""
    The `typing_json` library offers type-aware JSON encoding and decoding functionalities,
    on top of the ones offered by the builtin `json` library.

    The functions `typing_json.dump`, `typing_json.dumps`, `typing_json.load` and `typing_json.loads` mirror the
    functionality of their `json` counterparts, adding type-aware encoding/decoding and runtime type-checking of decoded objects.

    The types to be used for type-aware encoding/decoding and runtime type-checking are passed by the additional parameters `encoded_type`
    of `dump`/`dumps` and `decoded_type` of `load`/`loads`.
    Supported types include JSON basic types, `decimal.Decimal`, typed collections from the `typing` module, literal types, union types,
    optional types and (certain) typed namedtuples.
    For a complete list of supported types, see the documentation of `typing_json.encoding.is_json_encodable` from the `typing_json.encoding` module.

    The function `typing_json.typechecking.is_instance` (which can be imported directly as `from typing_json import is_instance`) extends the
    functionality of the builtin `isinstance` to include all the additional types supported by this library.

    The functions `typing_json.load` and `typing_json.loads` deviate from their `json` counterparts in that the default value for the optional
    `parse_float` parameter is `decimal.Decimal`, rather than `float`.
    The function `typing_json.typechecking.is_instance` deviates from the behaviour of the builtin `isinstance` on the literals `True`/`False`,
    which are not deemed of type `int`, and on integral instances of `decimal.Decimal`, which are deemed of type `int` if the optional parameter
    `cast_decimal` is set to `True` (its default value).

    (Version: 0.1.0)
"""

# standard imports
import collections
from decimal import Decimal
import json
from typing import Any, List, Tuple, Type

# internal imports
from typing_json.decoding import from_json_obj
from typing_json.encoding import is_json_encodable, to_json_obj
from typing_json.typechecking import is_instance, is_keyable, is_namedtuple, is_typecheckable


name: str = "typing_json"
__version__: str = "0.1.1.post1"

def dump(obj: Any, encoded_type: Type, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw) -> None:
    # pylint: disable = too-many-arguments
    """
        Encodes `obj` as a JSON object using `encoded_type` as a type hint, then calls `json.dump`.

        Raises `TypeError` is `encoded_type` is not JSON-encodable according to `typing_json.encoding.is_json_encodable`.
    """
    if not is_json_encodable(encoded_type):
        raise TypeError("Type %s is not json-encodable."%str(encoded_type))
    json_obj = to_json_obj(obj, encoded_type)
    return json.dump(json_obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kw)


def dumps(obj: Any, encoded_type: Type, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw) -> str:
    # pylint: disable = too-many-arguments
    """
        Encodes `obj` as a JSON object using `encoded_type` as a type hint, then calls `json.dumps`.

        Raises `TypeError` is `encoded_type` is not JSON-encodable according to `typing_json.encoding.is_json_encodable`.
    """
    if not is_json_encodable(encoded_type):
        raise TypeError("Type %s is not json-encodable."%str(encoded_type))
    json_obj = to_json_obj(obj, encoded_type)
    return json.dumps(json_obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kw)


def load(fp, decoded_type: Type, cast_decimal: bool = True, cls=None, parse_float=Decimal, parse_int=None, parse_constant=None, **kw) -> Any:
    # pylint: disable = too-many-arguments
    """
        Calls `json.load`, then decodes `obj` from the resulting JSON object using `decoded_type` as a type hint.

        Raises `TypeError` is `decoded_type` is not JSON-encodable according to `typing_json.encoding.is_json_encodable`.
    """
    if not is_json_encodable(decoded_type):
        raise TypeError("Type %s is not json-encodable."%str(decoded_type))
    obj = json.load(fp, cls=cls, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=collections.OrderedDict, **kw)
    return from_json_obj(obj, decoded_type, cast_decimal=cast_decimal)


def loads(s: str, decoded_type: Type, cast_decimal: bool = True, encoding=None, cls=None, parse_float=Decimal, parse_int=None, parse_constant=None, **kw) -> Any:
    # pylint: disable = too-many-arguments
    """
        Calls `json.load`, then decodes `obj` from the resulting JSON object using `decoded_type` as a type hint.

        Raises `TypeError` is `decoded_type` is not JSON-encodable according to `typing_json.encoding.is_json_encodable`.
    """
    if not is_json_encodable(decoded_type):
        raise TypeError("Type %s is not json-encodable."%str(decoded_type))
    obj = json.loads(s, encoding=encoding, cls=cls, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=collections.OrderedDict, **kw)
    return from_json_obj(obj, decoded_type, cast_decimal=cast_decimal)
