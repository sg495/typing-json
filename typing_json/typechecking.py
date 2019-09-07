""" Dynamic typechecking utilities. """
#pylint:disable=line-too-long

import textwrap
from typing import Any, Union, Optional, Callable
from collections import deque, OrderedDict
from collections.abc import Mapping
from typing_extensions import Literal

HASHABLE_BASE_TYPES = (bool, int, float, complex, str, bytes, range, type)

TYPECHECKABLE_BASE_TYPES = (bool, int, float, complex, str, bytes, bytearray, memoryview,
                            list, tuple, range, slice, set, frozenset, dict, type,
                            deque, OrderedDict, object)

_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."

def short_str(obj: Any) -> str:
    """ Returns a shortened string representation of objects for error messages. """
    return textwrap.shorten(str(obj), width=30, placeholder="...")

def is_hashable(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """ Returns True if the type is hashable. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    if t in HASHABLE_BASE_TYPES:
        return True
    if t in (None, type(None)):
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        if t.__origin__ in (frozenset, Union, Optional):
            if all(is_hashable(s) for s in t.__args__):
                return True
            if failure_callback:
                failure_callback("Not all type arguments of type %s are hashable."%str(t))
            return False
        if t.__origin__ is tuple:
            if len(t.__args__) == 2 and t.__args__[1] == ...:
                if is_hashable(t.__args__[0]):
                    return True
            else:
                if all(is_hashable(s) for s in t.__args__):
                    return True
            if failure_callback:
                failure_callback("Not all type arguments of type %s are hashable."%str(t))
            return False
        if t.__origin__ is Literal:
            if all(isinstance(s, HASHABLE_BASE_TYPES) or s is None for s in t.__args__):
                return True
            raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
    if is_namedtuple(t):
        return True
    if failure_callback:
        failure_callback("Type %s is not hashable."%str(t))
    return False

def is_typecheckable(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """ Returns True if is_instance is guaranteed to work with type t. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    if t in TYPECHECKABLE_BASE_TYPES:
        return True
    if t in (None, type(None), Any):
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        if t.__origin__ in (list, set, frozenset, dict,
                            deque, OrderedDict, Union, Optional, Mapping):
            if all(is_typecheckable(s) for s in t.__args__):
                return True
            if failure_callback:
                failure_callback("Not all type arguments of type %s are typecheckable."%str(t))
            return False
        if t.__origin__ is tuple:
            if len(t.__args__) == 2 and t.__args__[1] == ...:
                if is_typecheckable(t.__args__[0]):
                    return True
            else:
                if all(is_typecheckable(s) for s in t.__args__):
                    return True
            if failure_callback:
                failure_callback("Not all type arguments of type %s are typecheckable."%str(t))
            return False
        if t.__origin__ is Literal:
            if all(isinstance(s, TYPECHECKABLE_BASE_TYPES) or s in (None, Any) for s in t.__args__):
                return True
            raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
    if is_namedtuple(t):
        return True
    if failure_callback:
        failure_callback("Type %s is not typecheckable."%str(t))
    return False

def is_instance(obj: Any, t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """ Extends isinstance to support the typing package. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches,too-many-statements
    if t in TYPECHECKABLE_BASE_TYPES:
        if isinstance(obj, t):
            return True
        if failure_callback:
            failure_callback("Value %s is not of type %s."%(short_str(obj), str(t)))
        return False
    if t in (None, type(None)):
        if obj is None:
            return True
        if failure_callback:
            failure_callback("Value %s is not of type %s."%(short_str(obj), str(t)))
        return False
    if t == Any:
        return True
    if is_namedtuple(t):
        field_types = getattr(t, "_field_types")
        for field in field_types:
            if not hasattr(obj, field):
                if failure_callback:
                    failure_callback("Value %s is not of type %s: missing field %s."%(short_str(obj), str(t), field))
                return False
            field_val = getattr(obj, field)
            if not is_instance(field_val, field_types[field]):
                if failure_callback:
                    failure_callback("Value %s is not of type %s: wrong type %s for field %s, expected %s."%(short_str(obj), str(t), str(type(field_val)), field, str(field_types[field])))
                return False
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"): # generics
        if t.__origin__ is Union: # includes Optional
            if any(is_instance(obj, s) for s in t.__args__):
                return True
            if failure_callback:
                failure_callback("Value %s does not match any of the types in %s."%(short_str(obj), str(t)))
            return False
        if t.__origin__ is Literal:
            if any(obj is s for s in t.__args__):
                return True
            if failure_callback:
                failure_callback("Value %s does not match any of the values in %s."%(short_str(obj), str(t)))
            return False
        if t.__origin__ is list: # List[_T]
            if not isinstance(obj, list):
                if failure_callback:
                    failure_callback("Value %s is not a list."%short_str(obj))
                return False
            if all(is_instance(x, t.__args__[0]) for x in obj):
                return True
            if failure_callback:
                failure_callback("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])))
            return False
        if t.__origin__ is tuple: # Tuple[_T1, _T2, ... ,_TN] or Tuple[_T, Ellipsis]
            if not isinstance(obj, tuple):
                if failure_callback:
                    failure_callback("Value %s is not a tuple."%short_str(obj))
                return False
            if len(t.__args__) == 2 and t.__args__[1] is ...: # Tuple[_T, Ellipsis] # pylint:disable=no-else-return
                if all(is_instance(x, t.__args__[0]) for x in obj):
                    return True
                if failure_callback:
                    failure_callback("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])))
                return False
            else: # Tuple[_T1, _T2, ... ,_TN]
                if len(obj) != len(t.__args__):
                    if failure_callback:
                        failure_callback("Tuple %s is of the wrong length for type %s"%(short_str(obj), str(t)))
                    return False
                if all(is_instance(x, t.__args__[i]) for i, x in enumerate(obj)):
                    return True
                if failure_callback:
                    failure_callback("Not all values in %s are of the respective types specified by %s"%(short_str(obj), str(t)))
                return False
        if t.__origin__ is set: # Set[_T]
            if not isinstance(obj, set):
                if failure_callback:
                    failure_callback("Value %s is not a set."%short_str(obj))
                return False
            if all(is_instance(x, t.__args__[0]) for x in obj):
                return True
            if failure_callback:
                failure_callback("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])))
            return False
        if t.__origin__ is frozenset: # FrozenSet[_T]
            if not isinstance(obj, frozenset):
                if failure_callback:
                    failure_callback("Value %s is not a frozenset."%short_str(obj))
                return False
            if all(is_instance(x, t.__args__[0]) for x in obj):
                return True
            if failure_callback:
                failure_callback("Not all elements of %s are of type %s."%(short_str(obj), str(t.__args__[0])))
            return False
        if t.__origin__ is dict: # Dict[_T, _S]
            if not isinstance(obj, (dict)):
                if failure_callback:
                    failure_callback("Value %s is not a dict."%short_str(obj))
                return False
            if not all(is_instance(x, t.__args__[0]) for x in obj):
                if failure_callback:
                    failure_callback("Not all keys of %s are of type %s."%(short_str(obj), str(t.__args__[0])))
                return False
            if not all(is_instance(obj[x], t.__args__[1]) for x in obj):
                if failure_callback:
                    failure_callback("Not all values of %s are of type %s."%(short_str(obj), str(t.__args__[1])))
                return False
            return True
        if t.__origin__ is deque: # Deque[_T]
            if not isinstance(obj, deque):
                return False
            return all(is_instance(x, t.__args__[0]) for x in obj)
        if t.__origin__ is OrderedDict: # OrderedDict[_T, _S]
            if not isinstance(obj, (OrderedDict)):
                if failure_callback:
                    failure_callback("Value %s is not an OrderedDict."%short_str(obj))
                return False
            if not all(is_instance(x, t.__args__[0]) for x in obj):
                if failure_callback:
                    failure_callback("Not all keys of %s are of type %s."%(short_str(obj), str(t.__args__[0])))
                return False
            if not all(is_instance(obj[x], t.__args__[1]) for x in obj):
                if failure_callback:
                    failure_callback("Not all values of %s are of type %s."%(short_str(obj), str(t.__args__[1])))
                return False
            return True
        if t.__origin__ is Mapping: # Mapping[_T, _S]
            if not isinstance(obj, (dict, OrderedDict)):
                if failure_callback:
                    failure_callback("Value %s is not a dict or OrderedDict."%short_str(obj))
                return False
            if not all(is_instance(x, t.__args__[0]) for x in obj):
                if failure_callback:
                    failure_callback("Not all keys of %s are of type %s."%(short_str(obj), str(t.__args__[0])))
                return False
            if not all(is_instance(obj[x], t.__args__[1]) for x in obj):
                if failure_callback:
                    failure_callback("Not all values of %s are of type %s."%(short_str(obj), str(t.__args__[1])))
                return False
            return True
    raise TypeError("Type %s is not supported."%str(t))

def is_namedtuple(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """
        Checks whether a given type is a NamedTuple.
        Code modified from this stackoverflow question:
        https://stackoverflow.com/questions/2166818/how-to-check-if-an-object-is-an-instance-of-a-namedtuple
    """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches,protected-access
    if not hasattr(t, "__bases__"):
        if failure_callback:
            failure_callback("Type %s has no attribute __bases__."%str(t))
        return False
    base_classes = t.__bases__
    if len(base_classes) != 1 or base_classes[0] != tuple:
        if failure_callback:
            failure_callback("Attribute bases for type %s should be [tuple], found %s instead"%(str(t), str(t.__bases__)))
        return False
    if not hasattr(t, "_fields"):
        if failure_callback:
            failure_callback("Type %s has no attribute _fields."%str(t))
        return False
    fields = getattr(t, "_fields")
    if not isinstance(fields, tuple):
        if failure_callback:
            failure_callback("Attribute _fields for type %s should be a tuple, found %s instead."%(str(t), str(fields)))
        return False
    if not all(isinstance(n, str) for n in fields):
        if failure_callback:
            failure_callback("Attribute _fields for type %s should be a tuple of strings, found %s instead."%(str(t), str(fields)))
        return False
    if not hasattr(t, "_field_types"):
        if failure_callback:
            failure_callback("Type %s has no attribute _field_types."%str(t))
        return False
    field_types = getattr(t, "_field_types", None)
    if not isinstance(field_types, dict):
        if failure_callback:
            failure_callback("Attribute _field_types for type %s should be a dict, found %s instead."%(str(t), str(field_types)))
        return False
    for n in fields:
        if not n in field_types:
            if failure_callback:
                failure_callback("Field %s appears in _fields but not in _field_types for type %s."%(n, str(t)))
            return False
    for n in field_types:
        if not n in fields:
            if failure_callback:
                failure_callback("Field %s appears in _field_types but not in _fields for type %s."%(n, str(t)))
            return False
        if not is_typecheckable(field_types[n]):
            if failure_callback:
                failure_callback("Field %s for type %s has non-typecheckable field type %s."%(n, str(t), str(field_types[n])))
            return False
    if not hasattr(t, "_field_defaults"):
        if failure_callback:
            failure_callback("Type %s has no attribute _field_defaults."%str(t))
        return False
    field_defaults = getattr(t, "_field_defaults")
    if not isinstance(field_defaults, dict):
        if failure_callback:
            failure_callback("Attribute _field_types for type %s should be a dict, found %s instead."%(str(t), str(field_types)))
        return False
    for n in field_defaults:
        if not n in fields:
            if failure_callback:
                failure_callback("Field %s appears in _field_defaults but not in _fields for type %s."%(n, str(t)))
            return False
        if not is_instance(field_defaults[n], field_types[n]):
            if failure_callback:
                failure_callback("Default value for field %s of type %s should be of type %s, found type %s instead."%(n, str(t), str(field_types[n]), str(type(field_defaults[n]))))
            return False
    return True
