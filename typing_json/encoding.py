""" Encoding utilities """
# pylint:disable=line-too-long

from typing import Any, Union, Optional, Tuple, Callable, List
from collections import deque, OrderedDict
from collections.abc import Mapping
import json
from typing_extensions import Literal
from typing_json.typechecking import is_typecheckable, is_instance, is_namedtuple, is_hashable, short_str

JSON_BASE_TYPES: Tuple[type, ...] = (bool, int, float, str, type(None))
_UNREACHABLE_ERROR_MSG = "Should never reach this point, please open an issue on GitHub."

def is_json_encodable(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    """ Checks whether a type is json encodable. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    if not is_typecheckable(t, failure_callback):
        if failure_callback:
            failure_callback("Type %s is not typecheckable."%str(t))
        return False
    if t in JSON_BASE_TYPES:
        return True
    if t in (None, type(None)):
        return True
    if is_namedtuple(t):
        field_types = getattr(t, "_field_types")
        if all(is_json_encodable(field_types[field]) for field in field_types):
            return True
        if failure_callback:
            failure_callback("Not all fields of namedtuple %s are json-encodable."%str(t))
        return False
    if hasattr(t, "__origin__") and hasattr(t, "__args__"):
        if t.__origin__ in (list, set, frozenset, deque, Optional):
            if is_json_encodable(t.__args__[0]):
                return True
            if failure_callback:
                failure_callback("Type of elements in %s is not json-encodable."%str(t))
            return False
        if t.__origin__ is tuple:
            if len(t.__args__) == 2 and t.__args__[1] is ...: # pylint:disable=no-else-return
                if is_json_encodable(t.__args__[0]):
                    return True
                if failure_callback:
                    failure_callback("Type of elements in %s is not json-encodable."%str(t))
                return False
            else:
                if all(is_json_encodable(s) for s in t.__args__):
                    return True
                if failure_callback:
                    failure_callback("Type of some element in %s is not json-encodable."%str(t))
                return False
        if t.__origin__ is Union:
            if all(is_json_encodable(s) for s in t.__args__):
                return True
            if failure_callback:
                failure_callback("Some type in %s is not json-encodable."%str(t))
            return False
        if t.__origin__ in (dict, OrderedDict, Mapping):
            if not is_hashable(t.__args__[0]):
                if failure_callback:
                    failure_callback("Type of keys in %s is not hashable."%str(t))
                return False
            if not is_json_encodable(t.__args__[0]):
                if failure_callback:
                    failure_callback("Type of keys in %s is not json-encodable."%str(t))
                return False
            if not is_json_encodable(t.__args__[1]):
                if failure_callback:
                    failure_callback("Type of values in %s is not json-encodable."%str(t))
                return False
            return True
        if t.__origin__ is Literal:
            for s in t.__args__:
                if not isinstance(s, JSON_BASE_TYPES):
                    if failure_callback:
                        failure_callback("Value %s in literal type %s is not of basic json type."%(short_str(s), str(t)))
                    return False
            return True
    return False

def to_json_obj(obj: Any, t: Any) -> Any:
    """ Converts an json encodable type to a json standard type. """
    # pylint:disable=invalid-name,too-many-return-statements,too-many-branches
    trace: List[str] = []
    def failure_callback(message: str) -> None:
        trace.append(message)
    if not is_json_encodable(t, failure_callback):
        raise TypeError("Type %s is not json-encodable. Trace:\n%s"%(str(t), "\n".join(trace)))
    trace = []
    if not is_instance(obj, t, failure_callback):
        raise TypeError("Object %s is not of type %s. Trace:\n%s"%(short_str(obj), str(t), "\n".join(trace)))
    if t in JSON_BASE_TYPES:
        return obj
    if t in (None, type(None)):
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
        if t.__origin__ in (dict, Mapping):
            fields = [field for field in obj]
            if t.__args__[0] in JSON_BASE_TYPES:
                encoded_fields = [field for field in fields]
            else:
                encoded_fields = [json.dumps(to_json_obj(field, t.__args__[0])) for field in fields]
            return {encoded_fields[i]: to_json_obj(obj[field], t.__args__[1]) for i, field in enumerate(fields)}
        if t.__origin__ is OrderedDict:
            fields = [field for field in obj]
            if t.__args__[0] in JSON_BASE_TYPES:
                encoded_fields = [field for field in fields]
            else:
                encoded_fields = [json.dumps(to_json_obj(field, t.__args__[0])) for field in fields]
            new_ordered_dict = OrderedDict() # type:ignore
            for i, field in enumerate(fields):
                new_ordered_dict[encoded_fields[i]] = to_json_obj(obj[field], t.__args__[1])
            return new_ordered_dict
    raise AssertionError(_UNREACHABLE_ERROR_MSG) # pragma: no cover
