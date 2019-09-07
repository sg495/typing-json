""" Decoding utilities """
#pylint:disable=line-too-long

from typing import Any, Union, List
from collections import deque, OrderedDict
from collections.abc import Mapping
import json
from typing_extensions import Literal
from typing_json.typechecking import is_instance, is_namedtuple, short_str
from typing_json.encoding import JSON_BASE_TYPES, is_json_encodable

_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."

def from_json_obj(obj: Any, t: Any) -> Any:
    """ Converts an object of json standard type to json encodable type. """
    # pylint:disable=invalid-name,too-many-branches,too-many-statements,too-many-return-statements
    trace: List[str] = []
    def failure_callback(message: str) -> None:
        trace.append(message)
    if not is_json_encodable(t, failure_callback):
        raise TypeError("Type %s is not json-encodable. Trace:\n%s"%(str(t), "\n".join(trace)))
    if t in JSON_BASE_TYPES:
        if not isinstance(obj, t):
            raise TypeError("Object %s is not of json base type t=%s."%(short_str(obj), str(t)))
        return obj
    if t in (None, type(None)):
        if obj is not None:
            raise TypeError("Object %s is not None (t=%s)."%(short_str(obj), str(t)))
        return None
    if is_namedtuple(t):
        if not isinstance(obj, (dict, OrderedDict, list)):
            raise TypeError("Object %s is not (ordered) dictionary or list (t=%s)."%(short_str(obj), str(t))) # pylint:disable=line-too-long
        fields = getattr(t, "_fields")
        field_types = getattr(t, "_field_types")
        field_defaults = getattr(t, "_field_defaults")
        if isinstance(obj, list):
            if len(fields) != len(obj):
                raise TypeError("Object %s does not provide the right number of values for a namedtuple.")
            return_val = t(*tuple(from_json_obj(obj[i] if i < len(obj) else field_defaults[field], field_types[field]) for i, field in enumerate(fields))) # pylint:disable=line-too-long
            assert is_instance(return_val, t)
            return return_val
        converted_dict: OrderedDict() = {} # type:ignore
        if set(obj.keys()).union(set(field_defaults.keys())) != set(field_types.keys()):
            key_diff = set(obj.keys()).union(set(field_defaults.keys())) - set(field_types.keys())
            if key_diff:
                raise TypeError("Object %s does not have the required keys: t=%s, extra keys %s."%(short_str(obj), str(t), str(key_diff))) # pylint:disable=line-too-long
            key_diff = set(field_types.keys()) - set(obj.keys()).union(set(field_defaults.keys()))
            raise TypeError("Object %s does not have the required keys: t=%s, missing keys %s."%(short_str(obj), str(t), str(key_diff))) # pylint:disable=line-too-long
        for field in fields:
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
            raise TypeError("Object %s is not convertible to any of the types in %s."%(short_str(obj), str(t)))
        if t.__origin__ is Literal:
            trace = []
            if not is_instance(obj, t, failure_callback):
                raise TypeError("Object %s is not allowed (t=%s). Trace:\n%s"%(short_str(obj), str(t), "\n".join(trace)))
            return obj
        if t.__origin__ is list:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = list(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is deque:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = deque(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is set:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = set(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is frozenset:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            return_val = frozenset(from_json_obj(x, t.__args__[0]) for x in obj)
            assert is_instance(return_val, t)
            return return_val
        if t.__origin__ is tuple:
            if not isinstance(obj, list):
                raise TypeError("Object %s is not list (t=%s)."%(short_str(obj), str(t)))
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                return_val = tuple(from_json_obj(x, t.__args__[0]) for x in obj)
                assert is_instance(return_val, t)
                return return_val
            else:
                if len(obj) != len(t.__args__):
                    raise TypeError("List %s is of incorrect length (t=%s)."%(short_str(obj), str(t)))
                return_val = tuple(from_json_obj(x, t.__args__[i]) for i, x in enumerate(obj))
                assert is_instance(return_val, t)
                return return_val
        if t.__origin__ in (dict, Mapping):
            if not isinstance(obj, (dict, OrderedDict)):
                raise TypeError("Object %s is not dict or OrderedDict (t=%s)."%(short_str(obj), str(t)))
            converted_dict = dict() # type:ignore
            for field in obj:
                if t.__args__[0] in JSON_BASE_TYPES:
                    if not is_instance(field, t.__args__[0]):
                        raise TypeError("Object key %s is not of json base type %s (t=%s)."%(field, str(t.__args__[0]), str(t)))
                    converted_field = field
                else:
                    converted_field = from_json_obj(json.loads(field), t.__args__[0])
                converted_dict[converted_field] = from_json_obj(obj[field], t.__args__[1])
            assert is_instance(converted_dict, t)
            return converted_dict
        if t.__origin__ is OrderedDict:
            if not isinstance(obj, OrderedDict):
                raise TypeError("Object %s is not dict or OrderedDict (t=%s)."%(short_str(obj), str(t)))
            converted_dict = OrderedDict() # type:ignore
            for field in obj:
                if t.__args__[0] in JSON_BASE_TYPES:
                    if not isinstance(field, t.__args__[0]):
                        raise TypeError("Object key %s not of json base type %s (t=%s)."%(field, str(t.__args__[0]), str(t)))
                    converted_field = field
                else:
                    converted_field = from_json_obj(json.loads(field), t.__args__[0])
                converted_dict[converted_field] = from_json_obj(obj[field], t.__args__[1])
            assert is_instance(converted_dict, t)
            return converted_dict
    raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
