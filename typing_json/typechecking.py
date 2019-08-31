""" Dynamic typechecking utilities. """

import typing
from typing import Type

def is_namedtuple(named_tuple_type: Type) -> bool:
    """
        Checks whether a given type is a NamedTuple.
        Code modified from this stackoverflow question:
        https://stackoverflow.com/questions/2166818/how-to-check-if-an-object-is-an-instance-of-a-namedtuple
    """
    # pylint:disable=too-many-return-statements,protected-access
    base_classes = named_tuple_type.__bases__
    if len(base_classes) != 1 or base_classes[0] != tuple:
        return False
    fields = getattr(named_tuple_type, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    if not all(isinstance(n, str) for n in fields):
        return False
    field_types = getattr(named_tuple_type, '_field_types', None)
    if not isinstance(field_types, dict):
        return False
    if not all((n in field_types) for n in fields):
        return False
    if not all((n in fields) for n in field_types):
        return False
    if not all(isinstance(n, str) for n in field_types):
        return False
    if not all(isinstance(field_types[n], (type, typing._Final)) for n in field_types): #type:ignore
        return False
    field_defaults = getattr(named_tuple_type, '_field_defaults', None)
    if not isinstance(field_defaults, dict):
        return False
    if not all(isinstance(n, str) for n in field_defaults):
        return False
    if not all((n in fields) for n in field_defaults):
        return False
    if not all(isinstance(field_defaults[n], field_types[n]) for n in field_defaults):
        return False
    return True
