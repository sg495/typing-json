#pylint:disable = line-too-long, invalid-name
"""
    The `typing_json.encoding` provides functionality for type-aware JSON-encoding of objects.

    The core functionality is provided by `typing_json.encoding.to_json_obj`, which JSON-encodes instances
    of basic JSON types, typed collections from the `typing` module, literal types, union types, optional types
    and (certain) typed namedtuples.
    The JSON-encoding preserves all information necessary to reconstruct the at decoding time (cf. `typing_json.decoding.from_json_obj`).

    (Version: 0.1.0)
"""

# standard imports
from collections import deque, OrderedDict
from collections.abc import Mapping
from decimal import Decimal
from enum import EnumMeta
import json
from typing import Any, Callable, List, Optional, Union, Type

# external dependencies
from typing_extensions import Literal

# internal imports
from typing_json.typechecking import is_instance, is_keyable, is_namedtuple, is_typecheckable, JSON_BASE_TYPES, short_str


_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."


def _not_json_encodable(message: str, failure_callback: Optional[Callable[[str], None]]) -> Literal[False]:
    """ Utility message to fail (return `False`) by first calling an optional failure callback. """
    if failure_callback:
        failure_callback(message)
    return False


def is_json_encodable(t: Type, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """
        Checks whether a type `t` can be encoded into JSON (or decoded from JSON) using the `typing_json` library.

        The optional parameter `failure_callback` can be used to collect a detailed trace of
        the reasons behind this method returning `False` on a given type `t`.

        Currently, a type `t` is JSON encodable according to this method if it is typecheckable according to
        `typing_json.typechecking.is_typecheckable` and it satisfies one of the following conditions:

        - if `t` is one of the JSON basic types `bool`, `int`, `float`, `str`, `NoneType`;
        - if `t` is a `decimal.Decimal`;
        - if `t` is `None` (used as an alias for `NoneType`);
        - if `t` is an enum (i.e. `isinstance(t, EnumMeta)`);
        - if `t` is a namedtuple according to `typing_json.typechecking.is_namedtuple` and all its fields are JSON encodable;
        - if `t` is one of `typing.List`, `typing.Set`, `typing.FrozenSet`, `typing.Deque`, `typing.Optional` or a variadic `typing.Tuple` and its generic type argument is JSON encodable;
        - if `t` is a `typing.Union` or a fixed-length `typing.Tuple` and all of its generic type arguments are JSON encodable;
        - if `t` is a `typing.Dict`, `typing.OrderedDict` or `typing.Mapping`, its generic key type is keyable (according to `typing_json.typechecking.is_keyable`) and both its generic key and value types are JSON encodable;
        - if `t` is a `typing_extensions.Literal` and all of its literal arguments are of JSON basic type.

    """
    # pylint: disable = too-many-return-statements, too-many-branches
    if not is_typecheckable(t, failure_callback=failure_callback):
        # only typecheckable types are encodable
        return _not_json_encodable("Type %s is not typecheckable."%str(t), failure_callback=failure_callback)
    if t in JSON_BASE_TYPES:
        # JSON basic types are encodable
        return True
    if t is Decimal:
        # `decimal.Decimal` is encodable
        return True
    if t is None:
        # `None` canbe used as an alias for class `NoneType`
        return True
    if isinstance(t, EnumMeta):
        # enums are encodable
        return True
    if is_namedtuple(t):
        field_types = getattr(t, "_field_types")
        if all(is_json_encodable(field_types[field], failure_callback=failure_callback) for field in field_types):
            # namedtuples are encodable if all their fields are of encodable types
            return True
        return _not_json_encodable("Not all fields of namedtuple %s are json-encodable."%str(t), failure_callback=failure_callback)
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        # `typing` generics
        if t.__origin__ in (list, set, frozenset, deque, Optional):
            if is_json_encodable(t.__args__[0], failure_callback=failure_callback):
                # `typing.List`, `typing.Set`, `typing.FrozenSet`, `typing.Deque` and `typing.Optional` are encodable if their generic type argument is encodable
                return True
            return _not_json_encodable("Type of elements in %s is not json-encodable."%str(t), failure_callback=failure_callback)
        if t.__origin__ is tuple:
            # `typing.Tuple`
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                if is_json_encodable(t.__args__[0], failure_callback=failure_callback):
                    # variadic `typing.Tuple` are encodable if their generic type argument is encodable
                    return True
                return _not_json_encodable("Type of elements in %s is not json-encodable."%str(t), failure_callback=failure_callback)
            else:
                if all(is_json_encodable(s, failure_callback=failure_callback) for s in t.__args__):
                    # fixed-length `typing.Tuple` are encodable if all their generic type arguments are encodable
                    return True
                return _not_json_encodable("Type of some element in %s is not json-encodable."%str(t), failure_callback=failure_callback)
        if t.__origin__ is Union:
            if all(is_json_encodable(s, failure_callback=failure_callback) for s in t.__args__):
                # `typing.Union` are encodable if all their generic type arguments are encodable
                return True
            return _not_json_encodable("Some type in %s is not json-encodable."%str(t), failure_callback=failure_callback)
        if t.__origin__ in (dict, OrderedDict, Mapping):
            # `typing.Dict`, `typing.OrderedDict` and `typing.Mapping` are encodable if their generic key and value types are encodable and their key type is keyable
            if not is_keyable(t.__args__[0], failure_callback=failure_callback):
                return _not_json_encodable("Type of keys in %s is not keyable."%str(t), failure_callback=failure_callback)
            if not is_json_encodable(t.__args__[0], failure_callback=failure_callback):
                return _not_json_encodable("Type of keys in %s is not json-encodable."%str(t), failure_callback=failure_callback)
            if not is_json_encodable(t.__args__[1], failure_callback=failure_callback):
                return _not_json_encodable("Type of values in %s is not json-encodable."%str(t), failure_callback=failure_callback)
            return True
        if t.__origin__ is Literal:
            # `typing_extensions.Literal` are encodable as long as their literals are JSON basic types, which is always the case if they are typecheckable.
            return True
    return False


def to_json_obj(obj: Any, t: Type, use_decimal: bool = False) -> Any:
    """
        Encodes an instance `obj` of typecheckable type `t` into a JSON object.
        The optional `use_decimal` parameter can be used to specify that instances of
        `decimal.Decimal` can be used in the output: if `False`, they are converted to strings.
        This method raises `TypeError` if type `t` is not typecheckable according to `typing_json.typechecking.is_typecheckable`.
        This method raises `TypeError` if `obj` is not of type `t` according to `typing_json.typechecking.is_instance`.

        The optional parameter `failure_callback` can be used to collect a detailed trace of
        the reasons behind this method returning `False` on a given type `t`.

        Currently, this method acts as follows on an instance `obj` of type `t`:

        - if `t` is one of the JSON basic types `bool`, `int`, `float`, `str`, `NoneType`, the instance `obj` is returned unchanged;
        - if `t` is `decimal.Decimal` and `use_decimal` is `False` (default), `str(obj)` is returned;
        - if `t` is `decimal.Decimal` and `use_decimal` is `True`, `obj` is returned unchanged;
        - if `t` is `None` (used as an alias for `NoneType`), `None` is returned;
        - if `t` is an enum (i.e. `isinstance(t, EnumMeta)`), the enum value name `obj._name_` is returned;
        - if `t` is a namedtuple according to `typing_json.typechecking.is_namedtuple` and all its fields are JSON encodable, this method is called recursively on all field values and then an ordered dictionary is returned with the field names as names and the JSON-encoded field values as corresponding values;
        - if `t` is `typing.Union`, the generic type arguments in the union are tried one after the other until a `u` is found such that `is_instance(obj, u)`, then `obj` is JSON-encoded using `u` as its type.
        - if `t` is a `typing_extensions.Literal`, `obj` is returned unchanged;
        - if `t` is one of `typing.List`, `typing.Set`, `typing.FrozenSet`, `typing.Deque` or `typing.Tuple`, a list is returned containing the elements of the original collection, recursively JSON-encoded;
        - if `t` is a `typing.Dict` or `typing.Mapping`, a dictionary (`dict`) is returned with JSON-encoded values from the original dictionary/mapping, associated to either then JSON-encoded keys or a stringified version of the JSON-encoded keys (cf. below);
        - if `t` is `typing.OrderedDict`, an ordered dictionary (`collections.OrderedDict`) is returned with JSON-encoded values from the original dictionary/mapping, associated to either then JSON-encoded keys or a stringified version of the JSON-encoded keys (cf. below).

        In the case of dictionaries, it is not necessarily the case keys will be compatible with the JSON specification in their JSON-encoded form.
        When encoding dictionaries, the keys used in the encoding follow the following criteria:

        - if the key type is a JOSN basic type, `decimal.Decimal` or an enumeration type, the JSON encoding of the keys is used;
        - otherwise, the stringified version of the JSON encoding (using `json.dumps`) is used;

        Literals can only be of JSON basic type.

    """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    trace: List[str] = []
    def failure_callback(message: str) -> None:
        trace.append(message)
    if not is_json_encodable(t, failure_callback=failure_callback):
        # Argument `t` must be JSON encodable.
        raise TypeError("Type %s is not json-encodable. Trace:\n%s"%(str(t), "\n".join(trace)))
    trace = []
    if not is_instance(obj, t, failure_callback=failure_callback):
        # Argument `obj` must be an instance of argument `t`.
        raise TypeError("Object %s is not of type %s. Trace:\n%s"%(short_str(obj), str(t), "\n".join(trace)))
    if t in JSON_BASE_TYPES:
        # JSON basic types are returned unchanged.
        return obj
    if t is Decimal:
        # If `use_decimal` is `True`, `obj` is returned unchanged:
        if use_decimal:
            return obj
        # If `use_decimal` is `False` (default), instances of `decimal.Decimal` are encoded as strings.
        return str(obj)
    if t in (None, type(None)):
        # `None` can be used as an alias for `NoneType`.
        return None
    if isinstance(t, EnumMeta):
        # Enum values are encoded by their name.
        return obj._name_ # pylint:disable=protected-access
    if is_namedtuple(t):
        # Namedtuples are encoded as ordered dictionaries, with their fields as keys and the JSON-encoded field values as corresponding values.
        field_types = getattr(t, "_field_types")
        json_dict = OrderedDict() # type:ignore
        for field in field_types:
            json_dict[field] = to_json_obj(getattr(obj, field), field_types[field])
        return json_dict
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        # Generics from the `typing` module.
        if t.__origin__ is Union:
            # values in a `typing.Union` are JSON-encoded using the first type in the union that the object is found to be an instance of.
            for s in t.__args__:
                if is_instance(obj, s):
                    return to_json_obj(obj, s)
            raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
        if t.__origin__ is Literal:
            # `typing_extensions.Literal` are returned unchanged
            return obj
        if t.__origin__ in (list, set, frozenset, deque):
            # `typing.List`, `typing.Set`, `typing.FrozenSet` and `typing.Deque` are turned into lists, with their elements recursively JSON-encoded
            return [to_json_obj(x, t.__args__[0]) for x in obj]
        if t.__origin__ is tuple:
            # `typing.Tuple` are turned into lists, with their elements recursively JSON-encoded
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                return [to_json_obj(x, t.__args__[0]) for x in obj]
            else:
                return [to_json_obj(x, t.__args__[i]) for i, x in enumerate(obj)]
        if t.__origin__ in (dict, OrderedDict, Mapping):
            # `typing.Dict` and `typing.Mapping` are turned into dictionaries and `typing.OrderedDict` are turned into ordered dictionaries.
            # The values are recursively JSON-encoded. Keys require special handling.
            fields = [field for field in obj] # pylint: disable = unnecessary-comprehension
            if t.__args__[0] in JSON_BASE_TYPES+(Decimal, None,):
                # Keys of JSON basic types, `decimal.Decimal` and `None` are recursively JSON-encoded.
                # encoded_fields = [field for field in fields] # pylint: disable = unnecessary-comprehension
                encoded_fields = [to_json_obj(field, t.__args__[0]) for field in fields]
            elif (hasattr(t.__args__[0], "__origin__") and t.__args__[0].__origin__ is Literal):
                # Keys of `typing_extensions.Literal` types are recursively JSON-encoded.
                # encoded_fields = [field for field in fields] # pylint: disable = unnecessary-comprehension
                encoded_fields = [to_json_obj(field, t.__args__[0]) for field in fields]
            elif isinstance(t.__args__[0], EnumMeta):
                # Keys of enumeration types are recursively JSON-encoded.
                encoded_fields = [to_json_obj(field, t.__args__[0]) for field in fields]
            else:
                # Keys of any other type are recursively JSON-encoded and then JSON dumped to strings.
                encoded_fields = [json.dumps(to_json_obj(field, t.__args__[0])) for field in fields]
            if t.__origin__ in (dict, Mapping):
                # A `dict`is used for `typing.Dict` and `typing.Mapping`.
                return {encoded_fields[i]: to_json_obj(obj[field], t.__args__[1]) for i, field in enumerate(fields)}
            if t.__origin__ is OrderedDict:
                # A `collections.OrderedDict` is used for `typing.OrderedDict`.
                new_ordered_dict = OrderedDict() # type:ignore
                for i, field in enumerate(fields):
                    new_ordered_dict[encoded_fields[i]] = to_json_obj(obj[field], t.__args__[1])
                return new_ordered_dict
    raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
