#pylint:disable = line-too-long, invalid-name
"""
    The `typing_json.typechecking` module provides functionality for dynamic typechecking.

    The core functionality is provided by `typing_json.typechecking.is_instance`, which extends
    the builtin `isinstance` to deal with certain typed collections created using the `typing` module,
    as well as literal types, optional types, unions and (certain) typed namedtuples.

    (Version: 0.1.0)
"""

# standard imports
from collections import deque, OrderedDict
from collections.abc import Mapping
from decimal import Decimal
from enum import EnumMeta
import textwrap
from typing import Any, Callable, Optional, Tuple, Type, Union

# external dependencies
from typing_extensions import Literal


JSON_BASE_TYPES: Tuple[type, ...] = (bool, int, float, str, type(None))
""" Base types for JSON. """


KEYABLE_BASE_TYPES = (bool, int, float, Decimal, complex, str, bytes, range, type)
""" Base types that can be used for dictionary keys. """


TYPECHECKABLE_BASE_TYPES = (bool, int, float, Decimal, complex, str, bytes, bytearray, memoryview, list, tuple, range, slice, set, frozenset, dict, type, deque, OrderedDict, object)
""" Base types that can be typechecked. """


_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."


def _not_keyable(message: str, failure_callback: Optional[Callable[[str], None]]) -> Literal[False]:
    """ Utility message to fail (return `False`) by first calling an optional failure callback. """
    if failure_callback:
        failure_callback(message)
    return False


def is_keyable(t: Type, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """
        Check whether `t` is a type that can be used as a key when encoding/decoding mappings
        using this library.
        This function is used only in `typing_json.encoding.is_json_encodable`, to decided whether a
        mapping type is JSON encodable using this library.

        The optional parameter `failure_callback` can be used to collect a detailed trace of
        the reasons behind this method returning `False` on a given type `t`.

        At present, a type is keyable if it satisfies one of the following conditions:

        - it is one of `bool`, `int`, `float`, `decimal.Decimal`, `complex`, `str`, `bytes`, `range`, `type`;
        - it is `None` or an enumeration (i.e. `isinstance(t, EnumMeta)`);
        - it is a variadic `typing.Tuple`, a `typing.FrozenSet` or a `typing.Optional` and its generic type argument is keyable;
        - it is a fixed-length `typing.Tuple` or a `typing.Union` and all of its generic type arguments are keyable;
        - it is a `typing_extensions.Literal`;
        - it is a named tuple according to `typing_json.typechecking.is_namedtuple` and all of its fields are of keyable type.

    """
    # pylint: disable = too-many-return-statements, too-many-branches
    if t in KEYABLE_BASE_TYPES:
        # Types in the `KEYABLE_BASE_TYPES` collection are keyable.
        return True
    if t in (None, type(None)):
        # `None` is keyable.
        return True
    if isinstance(t, EnumMeta):
        # Enum types are keyable.
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        # Parametric types in the `typing` module.
        if t.__origin__ in (frozenset, Union, Optional):
            # The types `typing.FrozenSet`, `typing.Union` and `typing.Optional` are keyable
            # if all of their type arguments are keyable.
            if all(is_keyable(s, failure_callback=failure_callback) for s in t.__args__):
                return True
            return _not_keyable("Not all type arguments of type %s are keyable."%str(t), failure_callback=failure_callback)
        if t.__origin__ is tuple:
            # The type `typing.Tuple` is keyable if all of its type arguments are keyable.
            if len(t.__args__) == 2 and t.__args__[1] == ...:
                # This is the case of variadic `typing.Tuple`.
                if is_keyable(t.__args__[0], failure_callback=failure_callback):
                    return True
            else:
                # This is the case of fixed-length `typing.Tuple`.
                if all(is_keyable(s, failure_callback=failure_callback) for s in t.__args__):
                    return True
            return _not_keyable("Not all type arguments of type %s are keyable."%str(t), failure_callback=failure_callback)
        if t.__origin__ is Literal:
            # The type `typing_extensions.Literal` is keyable if all of its type arguments are keyable.
            # Currently, there is no way for this not to be the case, so this always returns true.
            if all(isinstance(s, KEYABLE_BASE_TYPES) or s is None for s in t.__args__):
                return True
            raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
    if is_namedtuple(t, check_keyable=True):
        # Types inheriting from `typing.NamedTuple` are keyable if all their fields have keyable type.
        return True
    return _not_keyable("Type %s is not keyable."%str(t), failure_callback=failure_callback)


def _not_typecheckable(message: str, failure_callback: Optional[Callable[[str], None]]) -> Literal[False]:
    """ Utility message to fail (return `False`) by first calling an optional failure callback. """
    if failure_callback:
        failure_callback(message)
    return False


def is_typecheckable(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """
        Checks whether `t` can be type-checked according to the `typing_json` library.
        This is a pre-requisite for `t` to be JSON encodable/decodable in the library.
        It is also a pre-requisite for all fields of types deemed to be namedtuples
        by `typing_json.typechecking.is_namedtuple`.

        The optional parameter `failure_callback` can be used to collect a detailed trace of
        the reasons behind this method returning `False` on a given type `t`.

        At present, a type is typecheckable if it satisfies one of the following conditions:

        - it is one of the basic typecheckable types: `bool`, `int`, `float`, `decimal.Decimal`, `complex`, `str`, `bytes`, `bytearray`, `memoryview`, `list`, `tuple`, `range`, `slice`, `set`, `frozenset`, `dict`, `type`, `collections.deque`, `collections.OrderedDict`, `object`;
        - it is `None`, `typing.Any` or an enumeration (i.e. `isinstance(t, EnumMeta)`);
        - it is one of `typing.List`, `typing.Set`, `typing.FrozenSet`, `typing.Deque`, `typing.Optional` or variadic `typing.Tuple` and its generic type argument is typecheckable;
        - it is one of `typing.Dict`, `typing.OrderedDict`, `typing.Mapping`, `typing.Union` or fixed-length `typing.Tuple` and all of its generic type arguments are typecheckable;
        - it is a `typing.Literal` including literals of one of the JSON basic types `bool`, `int`, `float`, `str` or `NoneType`;
        - it is a named tuple according to `typing_json.typechecking.is_namedtuple` and all of its fields are of typecheckable type.
    """
    # pylint: disable = too-many-return-statements, too-many-branches
    if t in TYPECHECKABLE_BASE_TYPES:
        # Types in the `TYPECHECKABLE_BASE_TYPES` collection are all typecheckable.
        return True
    if t in (None, type(None), Any):
        # `None` and `typing.Any` are typecheckable.
        return True
    if isinstance(t, EnumMeta):
        # Enum types are typecheckable.
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        # Parametric types in the `typing` module.
        if t.__origin__ in (list, set, frozenset, dict,
                            deque, OrderedDict, Union, Optional, Mapping):
            # The types `typing.List`, `typing.Set`, `typing.FrozenSet`, `typing.Dict`,
            # `typing.Deque`, `typing.OrderedDict`, `typing.Union` and `typing.Mapping`
            # are typecheckable if all of their type arguments are typecheckable.
            if all(is_typecheckable(s, failure_callback=failure_callback) for s in t.__args__):
                return True
            return _not_typecheckable("Not all type arguments of type %s are typecheckable."%str(t), failure_callback=failure_callback)
        if t.__origin__ is tuple:
            # The type `typing.Tuple` is typecheckable if all of its type arguments are typecheckable.
            if len(t.__args__) == 2 and t.__args__[1] == ...:
                # This is the case of variadic `typing.Tuple`.
                if is_typecheckable(t.__args__[0], failure_callback=failure_callback):
                    return True
            else:
                # This is the case of fixed-length `typing.Tuple`.
                if all(is_typecheckable(s, failure_callback=failure_callback) for s in t.__args__):
                    return True
            return _not_typecheckable("Not all type arguments of type %s are typecheckable."%str(t), failure_callback=failure_callback)
        if t.__origin__ is Literal:
            # The type `typing_extensions.Literal` is typecheckable if all of its type arguments are of JSON basic type.
            if all(isinstance(s, JSON_BASE_TYPES) for s in t.__args__):
                return True
            return _not_typecheckable("Not all type arguments of literal type %s are of JSON basic type."%str(t), failure_callback=failure_callback)
    if is_namedtuple(t, failure_callback=failure_callback):
        # Types inheriting from `typing.NamedTuple` are typecheckable, because `is_namedtuple` already
        # enforces fields to be of typecheckable type.
        return True
    return _not_typecheckable("Type %s is not typecheckable."%str(t), failure_callback=failure_callback)


def short_str(obj: Any) -> str:
    """ Returns a shortened string representation of `obj`, for use in error messages. """
    if isinstance(obj, str):
        return "\""+obj+"\""
    return textwrap.shorten(repr(obj), width=30, placeholder="...")


def _not_instance(message: str, failure_callback: Optional[Callable[[str], None]]) -> Literal[False]:
    """ Utility message to fail (return `False`) by first calling an optional failure callback. """
    if failure_callback:
        failure_callback(message)
    return False


def is_instance(obj: Any, t: Type, failure_callback: Optional[Callable[[str], None]] = None, cast_decimal: bool = True) -> bool:
    """
        Checks whether an object `obj` is an instance of type `t`, extending the dynamical typechecking capabilities of the
        builtin `isinstance` to some of the `typing` generics and to certain types constructed with `typing.NamedTuple`.
        On the basic typecheckable types (cf.&nbsp;`typing_json.typechecking.is_typecheckable`), it acts as the builtin `isinstance`,
        with tje following exceptions:

        - if the optional parameter `cast_decimal` is set to `True`, instances of `decimal.Decimal` are deemed to be instances of `float` (and `int` if integral) by this function;
        - the boolean literals `True` and `False` are not deemed of type `int` by this function (cf.&nbsp;https://www.python.org/dev/peps/pep-0285/).
        - instances of `int` are deemed to be instances of `float` by this function.

        The optional parameter `failure_callback` can be used to collect a detailed trace of the reasons behind this function returning `False` on a given object `obj` and type `t`.

        The optional parameter `cast_decimal` (default:&nbsp;`True`) can be used to specify that objects of type `decimal.Decimal`
        which encode integers have to be deemed of type `int` or `float`:

        ```python
            >>> from decimal import Decimal
            >>> is_instance(Decimal(1), int, cast_decimal=True)
            True
            >>> is_instance(Decimal(1.1), float, cast_decimal=True)
            True
            >>> is_instance(Decimal(1.1), int, cast_decimal=True)
            False
            >>> is_instance(Decimal(1), int, cast_decimal=False)
            False
            >>> is_instance(Decimal(1.1), float, cast_decimal=False)
            False
        ```

        Literals in `typing_extensions.Literal` can only be of one of the JSON basic types `bool`, `int`, `float`, `str`, `NoneType`.
    """
    # pylint: disable = too-many-return-statements, too-many-branches, too-many-statements
    if t in TYPECHECKABLE_BASE_TYPES:
        # for basic types, use builtin `isinstance`.
        if t == int and (obj is True or obj is False):
            # special case to deal with the fact that `bool` inherits from `int`, see https://www.python.org/dev/peps/pep-0285/
            return False
        if t == int and isinstance(obj, Decimal) and cast_decimal and obj == obj.to_integral_value():
            # special case to deal with `decimal.Decimal` being used to encode integers:
            return True
        if t == float and isinstance(obj, Decimal) and cast_decimal:
            # special case to deal with `decimal.Decimal` being used to encode floats:
            return True
        if t == float and isinstance(obj, int) and obj is not True and obj is not False:
            return True
        if isinstance(obj, t):
            return True
        return _not_instance("Value %s is not of type %s."%(short_str(obj), str(t)), failure_callback=failure_callback)
    if t in (None, type(None)):
        # for `None`, use `is None`.
        if obj is None:
            return True
        return _not_instance("Value %s is not of type %s."%(short_str(obj), str(t)), failure_callback=failure_callback)
    if t == Any:
        # For `typing.Any`, always return `True`.
        return True
    if isinstance(t, EnumMeta):
        # For enums, check whether `obj` is one of the values of the enumeration `t`.
        if obj in t.__members__.values(): # type: ignore
            return True
        return _not_instance("Value %s is not of enum type %s."%(short_str(obj), str(t)), failure_callback=failure_callback)
    if is_namedtuple(t, failure_callback=failure_callback):
        # For namedtuples, check that all fields are defined and have value of designated type.
        if obj.__class__ != t:
            return _not_instance("Value %s is not of type %s: wrong class %s."%(short_str(obj), str(t), str(obj.__class__)), failure_callback=failure_callback)
        field_types = getattr(t, "_field_types")
        for field in field_types:
            if not hasattr(obj, field):
                raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
                # return _not_instance("Value %s is not of type %s: missing field %s."%(short_str(obj), str(t), field), failure_callback=failure_callback)
            field_val = getattr(obj, field)
            if not is_instance(field_val, field_types[field], failure_callback=failure_callback, cast_decimal=cast_decimal):
                return _not_instance("Value %s is not of type %s: wrong type %s for field %s, expected %s."%(short_str(obj), str(t), str(type(field_val)), field, str(field_types[field])), failure_callback=failure_callback)
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        # Special cases for `typing` generics.
        if t.__origin__ is Union: # Union[T1, T2, ..., TN] or Optional[T]
            # For `typing.Union` (including `typing.Optional`), check that `obj` is instance of one of the type parameters of `typing.Union`.
            if any(is_instance(obj, s, failure_callback=failure_callback, cast_decimal=cast_decimal) for s in t.__args__):
                return True
            return _not_instance("Value %s does not match any of the types in %s."%(short_str(obj), str(t)), failure_callback=failure_callback)
        if t.__origin__ is Literal: # Literal[val1, val2, ..., valN]
            # For `typing_extensions.Literal`, check that `obj` equals one of the literals parameters of `typing_extensions.Literal`.
            if any(obj == s for s in t.__args__):
                return True
            return _not_instance("Value %s does not match any of the values in %s."%(short_str(obj), str(t)), failure_callback=failure_callback)
        if t.__origin__ is list: # List[T]
            # For `typing.List`, check that `obj` is a `list` and that all elements of `obj` are instances of the `typing.List` type parameter.
            if not isinstance(obj, list):
                return _not_instance("Value %s is not a list."%short_str(obj), failure_callback=failure_callback)
            if all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return True
            return _not_instance("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
        if t.__origin__ is tuple: # Tuple[T1, T2, ..., TN] or Tuple[T, ...] (with an actual ellipse `...` as the second type parameter of `typing.Tuple`)
            # For `typing.Tuple`, check that `obj` is a `tuple` and that all elements of `obj` are instances of the `typing.Tuple` type parameter(s).
            if not isinstance(obj, tuple):
                return _not_instance("Value %s is not a tuple."%short_str(obj), failure_callback=failure_callback)
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                # for variadic tuples, all elements have to be of the same type.
                if all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                    return True
                return _not_instance("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
            else:
                # for fixed-length tuples, each element has to be of the correct positional type.
                if len(obj) != len(t.__args__):
                    return _not_instance("Tuple %s is of the wrong length for type %s"%(short_str(obj), str(t)), failure_callback=failure_callback)
                if all(is_instance(x, t.__args__[i], failure_callback=failure_callback, cast_decimal=cast_decimal) for i, x in enumerate(obj)):
                    return True
                return _not_instance("Not all values in %s are of the respective types specified by %s"%(short_str(obj), str(t)), failure_callback=failure_callback)
        if t.__origin__ is set: # Set[T]
            # For `typing.Set`, check that `obj` is a `set` and that all elements of `obj` are instances of the `typing.Set` type parameter.
            if not isinstance(obj, set):
                return _not_instance("Value %s is not a set."%short_str(obj), failure_callback=failure_callback)
            if all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return True
            return _not_instance("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
        if t.__origin__ is frozenset: # FrozenSet[T]
            # For `typing.FrozenSet`, check that `obj` is a `frozenset` and that all elements of `obj` are instances of the `typing.FrozenSet` type parameter.
            if not isinstance(obj, frozenset):
                return _not_instance("Value %s is not a frozenset."%short_str(obj), failure_callback=failure_callback)
            if all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return True
            return _not_instance("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
        if t.__origin__ is deque: # Deque[T]
            # For `typing.Deque`, check that `obj` is a `deque` and that all elements of `obj` are instances of the `typing.Deque` type parameter.
            if not isinstance(obj, deque):
                return _not_instance("Value %s is not a deque."%short_str(obj), failure_callback=failure_callback)
            if all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return True
            return _not_instance("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
        if t.__origin__ is dict: # Dict[K,V]
            # For `typing.Dict`, check that `obj` is a `dict`,
            # check that all keys of `obj` are instances of the first `typing.Dict` type parameter,
            # and check that all values of `obj` are instances of the econd `typing.Dict` type parameter.
            if not isinstance(obj, (dict)):
                return _not_instance("Value %s is not a dict."%short_str(obj), failure_callback=failure_callback)
            if not all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return _not_instance("Not all keys of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
            if not all(is_instance(obj[x], t.__args__[1], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return _not_instance("Not all values of %s are of type %s."%(short_str(obj), str(t.__args__[1])), failure_callback=failure_callback)
            return True
        if t.__origin__ is OrderedDict: # OrderedDict[K,V]
            # For `typing.OrderedDict`, check that `obj` is a `collections.OrderedDict`,
            # check that all keys of `obj` are instances of the first `typing.OrderedDict` type parameter,
            # and check that all values of `obj` are instances of the econd `typing.OrderedDict` type parameter.
            if not isinstance(obj, (OrderedDict)):
                return _not_instance("Value %s is not an OrderedDict."%short_str(obj), failure_callback=failure_callback)
            if not all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return _not_instance("Not all keys of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
            if not all(is_instance(obj[x], t.__args__[1], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return _not_instance("Not all values of %s are of type %s."%(short_str(obj), str(t.__args__[1])), failure_callback=failure_callback)
            return True
        if t.__origin__ is Mapping: # Mapping[K,V], used for read-only dictionaries.
            # For `typing.Mapping`, check that `obj` is either a `dict` or a `collections.OrderedDict`,
            # check that all keys of `obj` are instances of the first `typing.Mapping` type parameter,
            # and check that all values of `obj` are instances of the econd `typing.Mapping` type parameter.
            if not isinstance(obj, (dict, OrderedDict)):
                return _not_instance("Value %s is not a dict or OrderedDict."%short_str(obj), failure_callback=failure_callback)
            if not all(is_instance(x, t.__args__[0], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return _not_instance("Not all keys of %s are of type %s."%(short_str(obj), str(t.__args__[0])), failure_callback=failure_callback)
            if not all(is_instance(obj[x], t.__args__[1], failure_callback=failure_callback, cast_decimal=cast_decimal) for x in obj):
                return _not_instance("Not all values of %s are of type %s."%(short_str(obj), str(t.__args__[1])), failure_callback=failure_callback)
            return True
    if failure_callback:
        failure_callback("Type %s is not supported."%str(t))
    raise TypeError("Type %s is not supported."%str(t))


def _not_namedtuple(message: str, failure_callback: Optional[Callable[[str], None]]) -> Literal[False]:
    """ Utility message to fail (return `False`) by first calling an optional failure callback. """
    if failure_callback:
        failure_callback(message)
    return False


def is_namedtuple(t: Type, failure_callback: Optional[Callable[[str], None]] = None, check_typecheckable: bool = True, check_keyable: bool = False, cast_decimal: bool = True) -> bool:
    """
        Checks whether `t` is a type constructed using `typing.NamedTuple`, using the following procedure:

        1. checks for existence of the attribute `t.__bases__`, containing the base classes of `t`;
        2. checks that there is exactly one base class in `t.__bases__`, namely `tuple`;
        3. checks for existence of the attribute `t._fields`, containing the fields names of`t`;
        4. checks that `t._fields` is a tuple of strings.
        5. checks for existence of the attribute `t._field_types`, containing the field types for `t`;
        6. checks that `t._field_tyes` is a dictionary with exactly the elements of `t._fields` as its keys;
        7. checks for the existence of the attribute `t._field_defaults`, containing the default values for fields of `t`;
        8. checks that `t._field_defaults` is a dictionary, and that all of its keys (if any) appear in `t._fields`;
        9. checks that all fields in `t._fields` also appear in `dir(t)`.

        The procedure above weeds out many incorrect examples, but certainly needs to be improved to catch all exceptions.

        If the optional parameter `check_typecheckable` is set to `True` (default: `True`), an additional check is added between 6. and 7. above
        for all field types to be typecheckable according to `typing_json.typechecking.is_typecheckable`.
        If the optional parameter `check_keyable` is set to `True` (default: `False`), an additional check is added between 6. and 7. above
        for all field types to be keyable according to `typing_json.typechecking.is_keyable`.
        If the optional parameter `check_typecheckable` is set to `True` (default: `True`), an additional check is added between 8. and 9. above
        for all field default values to be instances of the corresponding field types, according to `typing_json.typechecking.is_instance` (the value
        of the optional parameter `cast_decimal` is passed to `typing_json.typechecking.is_instance` when performing this check).
    """
    # pylint:disable = too-many-return-statements, too-many-branches, protected-access
    if not hasattr(t, "__bases__"):
        return _not_namedtuple("Type %s has no attribute __bases__."%str(t), failure_callback=failure_callback)
    base_classes = t.__bases__
    if len(base_classes) != 1 or base_classes[0] != tuple:
        return _not_namedtuple("Attribute bases for type %s should be [tuple], found %s instead"%(str(t), str(t.__bases__)), failure_callback=failure_callback)
    if not hasattr(t, "_fields"):
        return _not_namedtuple("Type %s has no attribute _fields."%str(t), failure_callback=failure_callback)
    fields = getattr(t, "_fields")
    if not isinstance(fields, tuple):
        return _not_namedtuple("Attribute _fields for type %s should be a tuple, found %s instead."%(str(t), str(fields)), failure_callback=failure_callback)
    if not all(isinstance(n, str) for n in fields):
        return _not_namedtuple("Attribute _fields for type %s should be a tuple of strings, found %s instead."%(str(t), str(fields)), failure_callback=failure_callback)
    if not hasattr(t, "_field_types"):
        return _not_namedtuple("Type %s has no attribute _field_types."%str(t), failure_callback=failure_callback)
    field_types = getattr(t, "_field_types", None)
    if not isinstance(field_types, dict):
        return _not_namedtuple("Attribute _field_types for type %s should be a dict, found %s instead."%(str(t), str(field_types)), failure_callback=failure_callback)
    for n in fields:
        if not n in field_types:
            return _not_namedtuple("Field %s appears in _fields but not in _field_types for type %s."%(n, str(t)), failure_callback=failure_callback)
    for n in field_types:
        if not n in fields:
            return _not_namedtuple("Field %s appears in _field_types but not in _fields for type %s."%(n, str(t)), failure_callback=failure_callback)
        if check_typecheckable and not is_typecheckable(field_types[n], failure_callback=failure_callback):
            return _not_namedtuple("Field %s for type %s has non-typecheckable field type %s."%(n, str(t), str(field_types[n])), failure_callback=failure_callback)
        if check_keyable and not is_keyable(field_types[n], failure_callback=failure_callback):
            return _not_namedtuple("Field %s for type %s has non-keyable field type %s."%(n, str(t), str(field_types[n])), failure_callback=failure_callback)
    if not hasattr(t, "_field_defaults"):
        return _not_namedtuple("Type %s has no attribute _field_defaults."%str(t), failure_callback=failure_callback)
    field_defaults = getattr(t, "_field_defaults")
    if not isinstance(field_defaults, dict):
        return _not_namedtuple("Attribute _field_types for type %s should be a dict, found %s instead."%(str(t), str(field_types)), failure_callback=failure_callback)
    for n in field_defaults:
        if not n in fields:
            return _not_namedtuple("Field %s appears in _field_defaults but not in _fields for type %s."%(n, str(t)), failure_callback=failure_callback)
        if check_typecheckable and not is_instance(field_defaults[n], field_types[n], failure_callback=failure_callback, cast_decimal=cast_decimal):
            return _not_namedtuple("Default value for field %s of type %s should be of type %s, found type %s instead."%(n, str(t), str(field_types[n]), str(type(field_defaults[n]))), failure_callback=failure_callback)
    for n in fields:
        if n not in dir(t):
            return _not_namedtuple("Field %s appears in _fields but not in dir(%s)."%(n, str(t)), failure_callback=failure_callback)
    return True
