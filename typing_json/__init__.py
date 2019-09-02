""" __init__ file for the typing_json package. """

from .typechecking import is_typecheckable, is_instance, is_namedtuple
from .encoding import is_json_encodable, to_json_obj
from .decoding import from_json_obj

name: str = "typing_json"
