""" Encoding utilities """

from typing import Any, Union, Optional, Tuple
from collections import deque, OrderedDict
from typing_extensions import Literal
from typing_json.typechecking import is_typecheckable, is_instance, is_namedtuple

JSON_BASE_TYPES: Tuple[type, ...] = (bool, int, float, str, type(None))
_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."

def is_json_encodable(t: Any) -> bool:
    """ Checks whether a type is json encodable. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    if not is_typecheckable(t):
        return False
    if t in JSON_BASE_TYPES:
        return True
    if t in (None, type(None)):
        return True
    if t is ...:
        return True
    if is_namedtuple(t):
        field_types = getattr(t, "_field_types")
        return all(is_json_encodable(field_types[field]) for field in field_types)
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        if t.__origin__ in (list, set, frozenset, deque, Optional):
            return is_json_encodable(t.__args__[0])
        if t.__origin__ is tuple:
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                return is_json_encodable(t.__args__[0])
            else:
                return all(is_json_encodable(s) for s in t.__args__)
        if t.__origin__ is Union:
            return all(is_json_encodable(s) for s in t.__args__)
        if t.__origin__ in (dict, OrderedDict):
            return t.__args__[0] == str and is_json_encodable(t.__args__[1])
        if t.__origin__ is Literal:
            return all(isinstance(s, JSON_BASE_TYPES+(type(None),)) for s in t.__args__)
    return False

def to_json_obj(obj: Any, t: Any) -> Any:
    """ Converts an json encodable type to a json standard type. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    if not is_json_encodable(t):
        raise TypeError("Type %s is not json-encodable."%str(t))
    if not is_instance(obj, t):
        raise TypeError("Object %s is not of type %s"%(str(obj), str(t)))
    if t in JSON_BASE_TYPES:
        return obj
    if t in (None, type(None), ...):
        return None
    if is_namedtuple(t):
        field_types = getattr(t, "_field_types")
        json_dict = OrderedDict() # type:ignore
        for field in field_types:
            json_dict[field] = to_json_obj(getattr(obj, field), field_types[field])
        return json_dict
    if hasattr(t, "__origin__") and hasattr(t, "__args__"): # generics
        if t.__origin__ is Union:
            for s in t.__args__:
                if is_instance(obj, s):
                    return to_json_obj(obj, s)
            raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
        if t.__origin__ is Literal:
            return obj
        if t.__origin__ in (list, set, frozenset, deque):
            return [to_json_obj(x, t.__args__[0]) for x in obj]
        if t.__origin__ is tuple:
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                return [to_json_obj(x, t.__args__[0]) for x in obj]
            else:
                return [to_json_obj(x, t.__args__[i]) for i, x in enumerate(obj)]
        if t.__origin__ is dict:
            return {field: to_json_obj(obj[field], t.__args__[1]) for field in obj}
        if t.__origin__ is OrderedDict:
            new_ordered_dict = OrderedDict() # type:ignore
            for field in obj:
                new_ordered_dict[field] = to_json_obj(obj[field], t.__args__[1])
            return new_ordered_dict
    raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
