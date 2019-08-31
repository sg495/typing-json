# typing-json
[![Build Status](https://api.travis-ci.com/sg495/typing-json.svg?branch=master)](https://travis-ci.com/sg495/typing-json)
[![Generic badge](https://img.shields.io/badge/python-3.7.4+-green.svg)](https://shields.io/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Generic badge](https://img.shields.io/badge/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Add typing support to python JSON serialization.


## typechecking module

The typechecking module contains utilities for dynamic typechecking which support relevant types from the typing and typing_extensions libraries.

### is_typecheckable

```python
def is_typecheckable(t: Any) -> bool:
    ...
````

The function `is_typecheckable(t)` from the `typing_json.typechecking` module returns `True` if and only if the `t` argument is one of the types supported for dynamic typechecking using the `is_instance(obj, t)` function from the same module. Currently supported types:

- the standard types `bool`, `int`, `float`, `complex`, `str`, `bytes`, `bytearray`, `memoryview`, `list`, `tuple`, `range`, `slice`, `set`, `frozenset`, `dict`, `type`, `None`, `Ellipsis`, `NotImplemented`;
- the `typing` types `List[_T]`, `Tuple[_T1,...]` (single-type variadic tuple), `Tuple[_T1,...,_TN]` (multi-type fixed arity tuple), `Set[_T]`, `FrozenSet[_T]`, `Dict[_T, _S]`, `OrderedDict[_T, _S]`, `Deque[_T]` where `_T`, `_S`, `_T1`, ..., `_TN` are themselves supported types;
- the `typing_extensions` type `Literal[_t1, ..., _tn]` where `_t1`, ..., `_tn` are immutable (comparison is performed using `obj is _tj`, not `obj == _tj`);
- types created using `typing.NamedTuple` using typecheckable field types;


### is_instance

```python
def is_instance(obj: Any, t: Any) -> bool:
    ...
````

The function `is_instance(obj, t)` from the `typing_json.typechecking` module returns `True` if and only if the `obj` argument is of type `t`. If `t` is not typecheckable according to `is_typecheckable(t)` then `ValueError` is raised.


### is_namedtuple

```python
def is_namedtuple(t: Any) -> bool:
    ...
```

The function `is_namedtuple(t)` from the `typing_json.typechecking` module returns `True` if the `obj` argument was created using `typing.NamedTuple` and all field types are typecheckable. It is currently possible to fool this method by using `collections.namedtuple` and manually adding a `_field_types:` dictionary with string keys and typecheckable types