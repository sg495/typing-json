""" Dynamic typechecking utilities. """

from typing import Any, Union, Optional
from collections import deque, OrderedDict
from typing_extensions import Literal

TYPECHECKABLE_BASE_TYPES = (bool, int, float, complex, str, bytes, bytearray, memoryview,
                            list, tuple, range, slice, set, frozenset, dict, type,
                            deque, OrderedDict, object)

def is_typecheckable(t: Any) -> bool:
    """ Returns True if is_instance is guaranteed to work with type t. """
    # pylint:disable=invalid-name
    if t in TYPECHECKABLE_BASE_TYPES:
        return True
    if t in (None, type(None), ..., NotImplemented, Any):
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        if t.__origin__ in (list, tuple, set, frozenset, dict,
                            deque, OrderedDict, Union, Optional):
            return all(is_typecheckable(s) for s in t.__args__)
        if t.__origin__ is Literal:
            return all(isinstance(s, TYPECHECKABLE_BASE_TYPES) or s in (None, ..., NotImplemented, Any) for s in t.__args__) # pylint:disable=line-too-long
    if is_namedtuple(t):
        return True
    return False

def is_instance(obj: Any, t: Any) -> bool:
    """ Extends isinstance to support the typing package. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    if t in TYPECHECKABLE_BASE_TYPES:
        return isinstance(obj, t)
    if t in (None, type(None)):
        return obj is None
    if t is ...:
        return obj is ...
    if t is NotImplemented:
        return obj is NotImplemented
    if t == Any:
        return True
    if is_namedtuple(t):
        field_types = getattr(t, "_field_types")
        for field in field_types:
            if not hasattr(obj, field):
                return False
            field_val = getattr(obj, field)
            if not is_instance(field_val, field_types[field]):
                return False
        return True
    if hasattr(t, "__origin__") and hasattr(t, "__args__"): # generics
        if t.__origin__ is Union: # includes Optional
            return any(is_instance(obj, s) for s in t.__args__)
        if t.__origin__ is Literal:
            return any(obj is s for s in t.__args__)
        if t.__origin__ is list: # List[_T]
            if not isinstance(obj, list):
                return False
            return all(is_instance(x, t.__args__[0]) for x in obj)
        if t.__origin__ is tuple: # Tuple[_T1, _T2, ... ,_TN] or Tuple[_T, Ellipsis]
            if not isinstance(obj, tuple):
                return False
            if len(t.__args__) == 2 and t.__args__[1] is ...: # Tuple[_T, Ellipsis] # pylint:disable=no-else-return
                return all(is_instance(x, t.__args__[0]) for x in obj)
            else: # Tuple[_T1, _T2, ... ,_TN]
                if len(obj) != len(t.__args__):
                    return False
                return all(is_instance(x, t.__args__[i]) for i, x in enumerate(obj))
        if t.__origin__ is set: # Set[_T]
            if not isinstance(obj, set):
                return False
            return all(is_instance(x, t.__args__[0]) for x in obj)
        if t.__origin__ is frozenset: # FrozenSet[_T]
            if not isinstance(obj, frozenset):
                return False
            return all(is_instance(x, t.__args__[0]) for x in obj)
        if t.__origin__ is dict: # Dict[_T, _S]
            if not isinstance(obj, (dict)):
                return False
            if not all(is_instance(x, t.__args__[0]) for x in obj):
                return False
            if not all(is_instance(obj[x], t.__args__[1]) for x in obj):
                return False
            return True
        if t.__origin__ is deque: # Deque[_T]
            if not isinstance(obj, deque):
                return False
            return all(is_instance(x, t.__args__[0]) for x in obj)
        if t.__origin__ is OrderedDict: # OrderedDict[_T, _S]
            if not isinstance(obj, (OrderedDict)):
                return False
            if not all(is_instance(x, t.__args__[0]) for x in obj):
                return False
            if not all(is_instance(obj[x], t.__args__[1]) for x in obj):
                return False
            return True
    raise TypeError("Type %s is not supported."%str(t))

def is_namedtuple(t: Any) -> bool:
    """
        Checks whether a given type is a NamedTuple.
        Code modified from this stackoverflow question:
        https://stackoverflow.com/questions/2166818/how-to-check-if-an-object-is-an-instance-of-a-namedtuple
    """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches,protected-access
    if not hasattr(t, "__bases__"):
        return False
    base_classes = t.__bases__
    if len(base_classes) != 1 or base_classes[0] != tuple:
        return False
    fields = getattr(t, "_fields", None)
    if not isinstance(fields, tuple):
        return False
    if not all(isinstance(n, str) for n in fields):
        return False
    field_types = getattr(t, "_field_types", None)
    if not isinstance(field_types, dict):
        return False
    if not all((n in field_types) for n in fields):
        return False
    if not all((n in fields) for n in field_types):
        return False
    if not all(is_typecheckable(field_types[n]) for n in field_types):
        return False
    field_defaults = getattr(t, "_field_defaults", None)
    if not isinstance(field_defaults, dict):
        return False
    if not all((n in fields) for n in field_defaults):
        return False
    if not all(is_instance(field_defaults[n], field_types[n]) for n in field_defaults):
        return False
    return True
