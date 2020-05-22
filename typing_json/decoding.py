#pylint:disable = line-too-long, invalid-name
"""
    The `typing_json.decoding` provides functionality for type-aware JSON-decoding of objects.

    The core functionality is provided by `typing_json.decoding.from_json_obj`, which can be used to
    turn JSON objects obtained from `typing_json.encoding.to_json_obj` back into instances of the original types.
    Types supported include JSON basic types, typed collections from the `typing` module, literal types, union types,
    optional types and (certain) typed namedtuples.

    (Version: 0.1.0)
"""

# standard imports
from collections import deque, OrderedDict
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from enum import EnumMeta
import json
from typing import Any, List, Union, Type

# external dependencies
from typing_extensions import Literal

# internal imports
from typing_json.typechecking import is_instance, is_namedtuple, JSON_BASE_TYPES, short_str
from typing_json.encoding import is_json_encodable


_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."


def from_json_obj(obj: Any, t: Type, cast_decimal: bool = True) -> Any:
    """
        Decodes a JSON object `obj` into an instance of a typecheckable type `t`.
        This method raises `TypeError` if type `t` is not JSON encodable according to `typing_json.encoding.is_json_encodable`.
        This method also raises `TypeError` if `obj` is not a valid JSON encoding for an instance of type `t`.

        Currently, this method acts as follows on an JSON object `obj` and a JSON-encodable type `t`:

        - if `t` is one of the JSON basic types `bool`, `float`, `str`, `NoneType`, `obj` must be an instance of the type an is returned unchanged;
        - if `t` is of the JSON basic type `int` and the `cast_decimal` parameter is set to `False`, `obj` must be an instance of `int` and is returned unchanged;
        - it `t` is of the JSON basic type `int` and the `cast_decimal` parameter is set to `True` (its default value), `obj` can be either an instance of `int`, in which case it is returned unchanged, or an instance of `decimal.Decimal` encoding an integer, in which case `int(obj)` is returned;
        - if `t` is of the JSON basic type `float` and the `cast_decimal` parameter is set to `False`, `obj` must be an instance of `int` or `float`, and `float(obj)` is returned;
        - it `t` is of the JSON basic type `float` and the `cast_decimal` parameter is set to `True` (its default value), `obj` can be either an instance of `int`, `float` or `decimal.Decimal`, in which case `float(obj)` is returned;
        - if `t` is `None`, used as an alias for `NoneType`, `obj` must be `None` and is returned unchanged;
        - if `t` is `decimal.Decimal` and the `cast_decimal` parameter is set to `False`, `obj` must be either a `decimal.Decimal`, an `int` or a `str` encoding a valid decimal, in which case `decimal.Decimal(obj)` is returned;
        v- if `t` is `decimal.Decimal` and the `cast_decimal` parameter is set to `True`, `obj` must be either a `decimal.Decimal`, an `int`, a `float` or a `str` encoding a valid decimal, in which case `decimal.Decimal(obj)` is returned;
        - if `t` is an enumeration, `obj` must be a key in the dictionary `t.__members__` of names for the enumeration constants, in which case `t.__members__[obj]` is returned;
        - if `t` is a namedtuple (according to `typing_json.typechecking.is_namedtuple`), see below;
        - if `t` is `typing.Union` or `typing.Optional`, try to decoded `obj` using the generic type arguments one after the other, until a suitable one is found;
        - if `t` is `typing_extensions.Literal`, check that `obj` is one of the literals and return it unaltered;
        - if `t` is `typing.List`, check that `obj` is a list and return a list with recursively JSON-decoded elements of `obj` in it;
        - if `t` is `typing.Tuple`, check that `obj` is a list and return a tuple with recursively JSON-decoded elements of `obj` in it;
        - if `t` is `typing.Deque`, check that `obj` is a list and return a deque with recursively JSON-decoded elements of `obj` in it;
        - if `t` is `typing.Set`, check that `obj` is a list and return a set with recursively JSON-decoded elements of `obj` in it;
        - if `t` is `typing.FrozenSet`, check that `obj` is a list and return a frozenset with recursively JSON-decoded elements of `obj` in it;
        - if `t` is `typing.Dict` or `typing.Mapping`, check that `obj` is a dict and return a dict with recursively JSON-decoded keys and values from `obj` (first parsing the keys from strings in all those cases where `typing_json.encoding.to_json_obj` would have stringified them);
        - if `t` is `typing.OrderedDict`, check that `obj` is a `collections.OrderedDict` and return a `collections.OrderedDict` with recursively JSON-decoded keys and values from `obj` (first parsing the keys from strings in all those cases where `typing_json.encoding.to_json_obj` would have stringified them);

        If `t` is a namedtuple (according to `typing_json.typechecking.is_namedtuple`), `obj` must be a dictionary (not necessarily ordered, although namedtuple are JSON-encoded as such).
        The keys for the dictionary must form a subset of all field names for the namedtuple `t`, including at least all names of fields without default value.
        An instance of `t` is then constructed (and returned) by assigning to fields having names in the dictionary the JSON decoding of the corresponding values in the dictionary, and to all other fields the default values specified by `t`.
    """
    # pylint: disable = too-many-branches, too-many-statements, too-many-return-statements
    trace: List[str] = []
    def failure_callback(message: str) -> None:
        trace.append(message)
    if not is_json_encodable(t, failure_callback=failure_callback):
        # Argument `t` must be JSON encodable.
        raise TypeError("Type %s is not json-encodable. Trace:\n%s"%(str(t), "\n".join(trace)))
    if t in JSON_BASE_TYPES:
        # JSON basic types are returned unaltered, with the exception of casting `Decimal` to `int`/`float` if `cast_decimal` is `True`.
        if t == int and cast_decimal and isinstance(obj, Decimal) and obj == obj.to_integral_value():
            return int(obj)
        if t == float and cast_decimal and isinstance(obj, Decimal):
            return float(obj)
        if t == float and isinstance(obj, int) and obj is not True and obj is not False:
            return float(obj)
        if not is_instance(obj, t, cast_decimal=cast_decimal):
            raise TypeError("Object %s is not of json basic type t=%s."%(short_str(obj), str(t)))
        return obj
    if t in (None, type(None)):
        # The only value of `NoneType` is `None`, which is returned unaltered.
        if obj is not None:
            raise TypeError("Object %s is not None (t=%s)."%(short_str(obj), str(t)))
        return None
    if t == Decimal:
        # Instances of `decimal.Decimal` are decoded from `int` or `string`, as well as from `float` if `cast_decimal` is `True`
        try:
            if isinstance(obj, (int, str, Decimal)) and obj is not True and obj is not False:
                return Decimal(obj)
            if cast_decimal and isinstance(obj, float) and obj is not True and obj is not False:
                return Decimal(obj)
        except InvalidOperation:
            ...
        raise TypeError("Object %s is not decimal.Decimal (t=%s)."%(short_str(obj), str(t)))
    if isinstance(t, EnumMeta):
        # For enumerations, use the `t.__members__` dictionary to convert the string name into an enumeration value.
        if not isinstance(obj, str):
            raise TypeError("Object %s is not a string (t=%s)."%(short_str(obj), str(t)))
        if obj not in t.__members__: # type: ignore
            raise TypeError("Object %s is not the string of a value of the enum (t=%s)."%(short_str(obj), str(t)))
        return t.__members__[obj] # type: ignore # pylint:disable=protected-access
    if is_namedtuple(t):
        # Namedtuples are decoded from dictionaries, not necessarily ordered (though they are encoded as ordered dictionaries).
        if not isinstance(obj, (dict, OrderedDict)):
            raise TypeError("Object %s is not (ordered) dictionary (t=%s)."%(short_str(obj), str(t))) # pylint:disable=line-too-long
        fields = getattr(t, "_fields")
        field_types = getattr(t, "_field_types")
        field_defaults = getattr(t, "_field_defaults")
        converted_dict: OrderedDict() = {} # type:ignore
        if set(obj.keys()).union(set(field_defaults.keys())) != set(field_types.keys()):
            # raise an error if the keys provided by the object together with the names of fields with default values don't yield exactly the names of all fields for the namedtuple
            key_diff = set(obj.keys()).union(set(field_defaults.keys())) - set(field_types.keys())
            if key_diff:
                raise TypeError("Object %s does not have the required keys: t=%s, extra keys %s."%(short_str(obj), str(t), str(key_diff))) # pylint:disable=line-too-long
            key_diff = set(field_types.keys()) - set(obj.keys()).union(set(field_defaults.keys()))
            raise TypeError("Object %s does not have the required keys: t=%s, missing keys %s."%(short_str(obj), str(t), str(key_diff))) # pylint:disable=line-too-long
        for field in fields:
            field_type = field_types[field]
            if not field in obj:
                # for each field not appearing in the JSON object, use the field default value
                converted_dict[field] = field_defaults[field]
            else:
                # for each field appearing in the JSON object, decoding the corresponding value
                converted_dict[field] = from_json_obj(obj[field], field_type)
        return_val = t(**converted_dict)
        assert is_instance(return_val, t, cast_decimal=cast_decimal)
        return return_val
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        # `typing` generics
        if t.__origin__ is Union:
            # For `typing.Union` (and `typing.Optional`), attempt to decode the value using the generic type arguments in sequence
            for s in t.__args__:
                try:
                    return_val = from_json_obj(obj, s)
                    assert is_instance(return_val, t, cast_decimal=cast_decimal)
                    return return_val
                except TypeError:
                    continue
            raise TypeError("Object %s is not convertible to any of the types in %s."%(short_str(obj), str(t)))
        if t.__origin__ is Literal:
            # for `typing_extensions.Literal`, check that the object is an instance of `t` and then return it unaltered
            trace = []
            if not is_instance(obj, t, failure_callback=failure_callback, cast_decimal=cast_decimal):
                raise TypeError("Object %s is not allowed (t=%s). Trace:\n%s"%(short_str(obj), str(t), "\n".join(trace)))
            return obj
        if t.__origin__ is list:
            # for `typing.List`, expect a list and return a list with recursively JSON-decoded elements
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = list(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t, cast_decimal=cast_decimal)
            return return_val
        if t.__origin__ is deque:
            # for `typing.Deque`, expect a list and return a deque with recursively JSON-decoded elements
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = deque(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t, cast_decimal=cast_decimal)
            return return_val
        if t.__origin__ is set:
            # for `typing.Set`, expect a list and return a set with recursively JSON-decoded elements
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = set(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t, cast_decimal=cast_decimal)
            return return_val
        if t.__origin__ is frozenset:
            # for `typing.FrozenSet`, expect a list and return a frozenset with recursively JSON-decoded elements
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = frozenset(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t, cast_decimal=cast_decimal)
            return return_val
        if t.__origin__ is tuple:
            # for `typing.Tuple`, expect a list and return a tuple with recursively JSON-decoded elements
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                return_val = tuple(from_json_obj(x, t.__args__[0]) for x in obj)
                assert is_instance(return_val, t, cast_decimal=cast_decimal)
                return return_val
            else:
                if len(obj) != len(t.__args__):
                    raise TypeError("List %s is of incorrect length (t=%s)."%(short_str(obj), str(t)))
                return_val = tuple(from_json_obj(x, t.__args__[i]) for i, x in enumerate(obj))
                assert is_instance(return_val, t, cast_decimal=cast_decimal)
                return return_val
        if t.__origin__ in (dict, Mapping):
            # for `typing.Dict` and `typing.Mapping`, expect a dict and return a dict with recursively JSON-decoded values and keys (parsing keys from strings in all those cases where they would have been stringified)
            if not isinstance(obj, (dict, OrderedDict)):
                raise TypeError("Object %s is not dict or OrderedDict (t=%s)."%(short_str(obj), str(t)))
            converted_dict = dict() # type:ignore
            for field in obj:
                if t.__args__[0] in JSON_BASE_TYPES:
                    if not is_instance(field, t.__args__[0], cast_decimal=cast_decimal):
                        raise TypeError("Object key %s is not of json basic type %s (t=%s)."%(field, str(t.__args__[0]), str(t)))
                    converted_field = field
                elif isinstance(t.__args__[0], EnumMeta) or hasattr(t.__args__[0], "__origin__") and t.__args__[0].__origin__ is Literal:
                    converted_field = from_json_obj(field, t.__args__[0])
                else:
                    converted_field = from_json_obj(json.loads(field), t.__args__[0])
                converted_dict[converted_field] = from_json_obj(obj[field], t.__args__[1])
            assert is_instance(converted_dict, t, cast_decimal=cast_decimal)
            return converted_dict
        if t.__origin__ is OrderedDict:
            # for `typing.OrderedDict`, expect a `collections.OrderedDict` and return an ordered dict with recursively JSON-decoded values and keys (parsing keys from strings in all those cases where they would have been stringified)
            if not isinstance(obj, OrderedDict):
                raise TypeError("Object %s is not OrderedDict (t=%s)."%(short_str(obj), str(t)))
            converted_dict = OrderedDict() # type:ignore
            for field in obj:
                if t.__args__[0] in JSON_BASE_TYPES:
                    if not isinstance(field, t.__args__[0]):
                        raise TypeError("Object key %s not of json basic type %s (t=%s)."%(field, str(t.__args__[0]), str(t)))
                    converted_field = field
                elif isinstance(t.__args__[0], EnumMeta) or hasattr(t.__args__[0], "__origin__") and t.__args__[0].__origin__ is Literal:
                    converted_field = from_json_obj(field, t.__args__[0])
                else:
                    converted_field = from_json_obj(json.loads(field), t.__args__[0])
                converted_dict[converted_field] = from_json_obj(obj[field], t.__args__[1])
            assert is_instance(converted_dict, t, cast_decimal=cast_decimal)
            return converted_dict
    raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
