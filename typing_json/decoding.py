""" Decoding utilities """

from typing import Any, Union
from collections import deque, OrderedDict
from typing_extensions import Literal
from typing_json.typechecking import is_instance, is_namedtuple
from typing_json.encoding import JSON_BASE_TYPES, is_json_encodable

_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."

def from_json_obj(obj: Any, t: Any) -> Any:
    """ Converts an object of json standard type to json encodable type. """
    # pylint:disable=invalid-name,too-many-branches,too-many-statements,too-many-return-statements
    if not is_json_encodable(t):
        raise TypeError("Type %s is not json-encodable."%str(t))
    if t in JSON_BASE_TYPES:
        if not isinstance(obj, t):
            raise TypeError("Object %s is not %s."%(str(obj), str(t)))
        return obj
    if t in (None, type(None)):
        if obj is not None:
            raise TypeError("Object %s is not null (t=%s)."%(str(obj), str(t)))
        return None
    if t is ...:
        if obj is not None:
            raise TypeError("Object %s is not null (t=%s)."%(str(obj), str(t)))
        return ...
    if is_namedtuple(t):
        if not isinstance(obj, (dict, OrderedDict)):
            raise TypeError("Object %s is not dictionary (t=%s)."%(str(obj), str(t)))
        field_types = getattr(t, "_field_types")
        converted_dict: OrderedDict() = {} # type:ignore
        field_defaults = getattr(t, "_field_defaults")
        if set(obj.keys()).union(set(field_defaults.keys())) != set(field_types.keys()):
            raise TypeError("Object %s does not have the required keys (t=%s)."%(str(obj), str(t)))
        for field in field_types:
            field_type = field_types[field]
            if not field in obj:
                converted_dict[field] = field_defaults[field]
            else:
                converted_dict[field] = from_json_obj(obj[field], field_type)
        return_val = t(**converted_dict)
        assert is_instance(return_val, t)
        return return_val
    if hasattr(t, "__origin__") and hasattr(t, "__args__"): # generics
        if t.__origin__ is Union:
            for s in t.__args__:
                try:
                    return_val = from_json_obj(obj, s)
                    assert is_instance(return_val, t)
                    return return_val
                except TypeError:
                    continue
            raise TypeError("Object %s is not convertible to any of %s."%(str(obj), str(t)))
        if t.__origin__ is Literal:
            if not is_instance(obj, t):
                raise TypeError("Object %s is not allowed (t=%s)."%(str(obj), str(t)))
            return obj
        if t.__origin__ is list:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(str(obj), str(t)))
            return_val = list(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is deque:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(str(obj), str(t)))
            return_val = deque(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is set:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(str(obj), str(t)))
            return_val = set(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is frozenset:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(str(obj), str(t)))
            return_val = frozenset(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is tuple:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(str(obj), str(t)))
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                return_val = tuple(from_json_obj(x, t.__args__[0]) for x in obj)
                assert is_instance(return_val, t)
                return return_val
            else:
                if len(obj) != len(t.__args__):
                    raise TypeError("List %s is of incorrect length (t=%s)."%(str(obj), str(t)))
                return_val = tuple(from_json_obj(x, t.__args__[i]) for i, x in enumerate(obj))
                assert is_instance(return_val, t)
                return return_val
        if t.__origin__ is dict:
            if not isinstance(obj, (dict, OrderedDict)):
                raise TypeError("Object %s is not dict or OrderedDict (t=%s)."%(str(obj), str(t)))
            converted_dict = dict() # type:ignore
            for field in obj:
                if not isinstance(field, str):
                    raise TypeError("Object key %s is string (t=%s)."%(field, str(t)))
                converted_dict[field] = from_json_obj(obj[field], t.__args__[1])
            assert is_instance(converted_dict, t)
            return converted_dict
        if t.__origin__ is OrderedDict:
            if not isinstance(obj, OrderedDict):
                raise TypeError("Object %s is not dict or OrderedDict (t=%s)."%(str(obj), str(t)))
            converted_dict = OrderedDict() # type:ignore
            for field in obj:
                if not isinstance(field, str):
                    raise TypeError("Object key %s is string (t=%s)."%(field, str(t)))
                converted_dict[field] = from_json_obj(obj[field], t.__args__[1])
            assert is_instance(converted_dict, t)
            return converted_dict
    raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
