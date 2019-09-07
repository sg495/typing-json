""" __init__ file for the typing_json package. """
# pylint:disable=line-too-long,too-many-arguments,invalid-name

import json
import collections
from typing import Any, List, Tuple
from .typechecking import is_hashable, is_typecheckable, is_instance, is_namedtuple
from .encoding import is_json_encodable, to_json_obj
from .decoding import from_json_obj

name: str = "typing_json"
__version__: str = "0.0.6"

def dump(obj: Any, encoded_type: Any, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw):
    """ Calls json.dump after encoding obj (of json-encodable type encoded_type) as a json object. """
    if not is_json_encodable(encoded_type):
        raise TypeError("Type %s is not json-encodable."%str(encoded_type))
    json_obj = to_json_obj(obj, encoded_type)
    return json.dump(json_obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kw)

def dumps(obj: Any, encoded_type: Any, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw):
    """ Calls json.dumps after encoding obj (of json-encodable type encoded_type) as a json object. """
    if not is_json_encodable(encoded_type):
        raise TypeError("Type %s is not json-encodable."%str(encoded_type))
    json_obj = to_json_obj(obj, encoded_type)
    return json.dumps(json_obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kw)


def load(fp, decoded_type: Any, cls=None, parse_float=None, parse_int=None, parse_constant=None, **kw):
    """ Calls json.load and then decodes the result into a json-encodable type. """
    if not is_json_encodable(decoded_type):
        raise TypeError("Type %s is not json-encodable."%str(decoded_type))
    obj = json.load(fp, cls=cls, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=collections.OrderedDict, **kw)
    return from_json_obj(obj, decoded_type)

def loads(s: str, decoded_type: Any, encoding=None, cls=None, parse_float=None, parse_int=None, parse_constant=None, **kw):
    """ Calls json.loads and then decodes the result into a json-encodable type. """
    if not is_json_encodable(decoded_type):
        raise TypeError("Type %s is not json-encodable."%str(decoded_type))
    obj = json.loads(s, encoding=encoding, cls=cls, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=collections.OrderedDict, **kw)
    return from_json_obj(obj, decoded_type)
