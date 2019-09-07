# typing-json
[![Build Status](https://api.travis-ci.com/sg495/typing-json.svg?branch=master)](https://travis-ci.com/sg495/typing-json)
[![codecov](https://codecov.io/gh/sg495/typing-json/graph/badge.svg)](https://codecov.io/gh/sg495/typing-json/)
[![Generic badge](https://img.shields.io/badge/python-3.7.4+-green.svg)](https://shields.io/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/typing-json.svg)](https://pypi.python.org/pypi/typing-json/)
[![PyPI status](https://img.shields.io/pypi/status/typing-json.svg)](https://pypi.python.org/pypi/typing-json/)
[![Generic badge](https://img.shields.io/badge/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Add typing support to python JSON serialization.

## typechecking

The typechecking module contains utilities for dynamic typechecking which support relevant types from the typing and typing_extensions libraries.

### is_hashable

```python
def is_hashable(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    ...
````

The function `is_hashable(t)` returns `True` if and only if the `t` argument is one of the types considered to be hashable for the purposes of dynamic typechecking in this package. Types currently deemed to be hashable by this function:

- the standard types `bool`, `int`, `float`, `complex`, `str`, `bytes`, `range`, `slice`, `type` and `NoneType` (as well as the value `None`, treated equivalently to `NoneType`);
- the `typing` types `Tuple[_T1,...]` (single-type variadic tuple), `Tuple[_T1,...,_TN]` (multi-type fixed arity tuple), `FrozenSet[_T]`, `Optional[_T]`, `Union[_T1,...,_TN]` where `_T`, `_S`, `_T1`, ..., `_TN` are themselves hashable types;
- the `typing_extensions` type `Literal[_v1, ..., _vn]` where `_v1`, ..., `_vn` are of hashable standard type (see above);
- types created using `typing.NamedTuple` using hashable field types;

Support for enum types and NewType is planned (see pull request [#5](https://github.com/sg495/typing-json/pull/5)).

If present, `failure_callback` is called to log all reasons why `t` fails to be hashable, in the order in which they arise.



### is_typecheckable

```python
def is_typecheckable(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    ...
````

The function `is_typecheckable(t)` returns `True` if and only if the `t` argument is one of the types supported for dynamic typechecking using the `is_instance(obj, t)` function from the same module. Currently supported types:

- the standard types `bool`, `int`, `float`, `complex`, `str`, `bytes`, `bytearray`, `memoryview`, `list`, `tuple`, `range`, `slice`, `set`, `frozenset`, `dict`, `type`, `NoneType` and `object` (as well as the value `None`, treated equivalently to `NoneType`);
- the `collections` types `deque` and `OrderedDict`;
- the `typing` types `Any`, `List[_T]`, `Tuple[_T1,...]` (single-type variadic tuple), `Tuple[_T1,...,_TN]` (multi-type fixed arity tuple), `Set[_T]`, `FrozenSet[_T]`, `Dict[_T, _S]`, `OrderedDict[_T, _S]`, `Mapping[_T, _S]`, `Deque[_T]`, `Optional[_T]`, `Union[_T1,...,_TN]` where `_T`, `_S`, `_T1`, ..., `_TN` are themselves supported types;
- the `typing_extensions` type `Literal[_v1, ..., _vn]` where `_v1`, ..., `_vn` are of typecheckable standard of `collections` type (see above);
- types created using `typing.NamedTuple` using typecheckable field types;

Arbitrary classes are currently not supported, regardless of type annotations. Support for types created using `collections.namedtuple` is not planned. Support for enum types and NewType is planned (see pull request [#5](https://github.com/sg495/typing-json/pull/5)).

If present, `failure_callback` is called to log all reasons why `t` fails to be typecheckable, in the order in which they arise.



### is_instance

```python
def is_instance(obj: Any, t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    ...
````

The function `is_instance(obj, t)` returns `True` if and only if the `obj` argument is of type `t`. If `t` is not typecheckable according to `is_typecheckable(t)` then `TypeError` is raised.

If present, `failure_callback` is called to log all reasons why `obj` fails to be an instance of `t`, in the order in which they arise.



### is_namedtuple

```python
def is_namedtuple(t: Any) -> bool:
    ...
```

The function `is_namedtuple(t)` returns `True` if the `obj` argument was created using `typing.NamedTuple` and all field types are typecheckable. It is currently possible to fool this method by using `collections.namedtuple` and manually adding a `_field_types:` dictionary with string keys and typecheckable types.

If present, `failure_callback` is called to log all reasons why `t` fails to be a NamedTuple, in the order in which they arise.


## encoding

### is_json_encodable

```python
def is_json_encodable(t: Any, failure_callback: Optional[Callable[[str], None]] = None) -> bool:
    ...
````

The function `is_json_encodable(t)` returns `True` if and only if `t` is a json-encodable type according to this package. At present, the following are json-encodable types:

- the standard types `bool`, `int`, `float`, `str`, and `NoneType` (as well as the value `None`, treated equivalently to `NoneType`);
- any `t` such that `is_namedtuple(t)` and such that all field types are json-encodable themselves;
- the `typing` types `List[_T]`, `Set[_T]`, `FrozenSet[_T]`, `Deque[_T]`, `Tuple[_T,...]`, `Tuple[_T1,...,_TN]`, `Dict[str, _T]`, `OrderedDict[str, _T]`, `Mapping[str, _T]`, `Union[_T1,...,_TN]`, `Optional[_T]`where `_T`, `_T1`, ..., `_TN` are themselves json-encodable types;
- the `typing_extensions` type `Literal[_v1,...,_vn]`, where where each `_vj in [_v1,...,_vn]` is of type `bool`, `int`, `float`, `str` or `NoneType`.

Future support is planned for more `typing` and `typing_extensions` types, including enum types and NewType (see pull request [#5](https://github.com/sg495/typing-json/pull/5)).

If present, `failure_callback` is called to log all reasons why `t` fails to be json-encodable, in the order in which they arise.


### to_json_obj

```python
def to_json_obj(obj: Any, t: Any) -> Any:
    ...
````

The function `to_json_obj(obj, t)` takes an object `obj` and a json encodable type `t` and converts `obj` into a natively--json-compatible object with the same fields and types. The conversion goes as follows:

- if `t in (bool, int, float, str)`, `obj` is returned unaltered;
- if `t in (None, NoneType, ...)`, `None` is returned;
- if `is_namedtuple(t)`, a `collections.OrderedDict` is returned with the fields of the named tuple as keys and respective values recursively converted to natively--json-compatible;
- if `t` is `Union[_T1,...,_TN]`, `obj` is converted to natively--json-compatible type according to the first type `_Tj` in the sequence `_T1`,...,`_TN` such that `is_instance(obj, _Tj)`;
- the type `Optional[_T]` is treated as `Union[_T, NoneType]`;
- if `t` is `Literal[_v1,...,_vN]`, `obj` is returned unaltered;
- if `t` is one of `List[_T]`, `Set[_T]`, `FrozenSet[_T]`, `Deque[_T]`, `Tuple[_T,...]` a list is returned, containing all elements of `obj` recursively converted to natively--json-compatible objects using type `_T` for the conversion;
- if `t` is `Tuple[_T1,...,_TN]`, a list is returned, containing all elements of `obj` recursively converted to natively--json-compatible objects using types `_T1`,...,`_TN` for the conversion of the elements `x1`,...,`xN` of `obj`;
- if `t` is `Dict[_S, _T]` or `Mapping[_S, _T]`, a dictionary is returned with keys and values recursively converted to natively--json-compatible type according to types `_S` and `_T` respectively, and the string version of the keys json is used if they are not one of `bool`, `int`, `float`, `str` or `NoneType`;
- if `t` is `OrderedDict[_S, _T]`, an dictionary is returned with keys and values recursively converted to natively--json-compatible type according to types `_S` and `_T` respectively, and the string version of the keys json is used if they are not one of `bool`, `int`, `float`, `str` or `NoneType`;

If `t` is not json-encodable according to `is_json_encodable(t)` then `TypeError` is raised. If `obj` is not of type `t` according to `is_instance(obj, t)` then `TypeError` is raised.

For the purposes of this library, natively--json-compatible types are: `bool`, `int`, `float`, `str`, `NoneType`, `list`, `dict` and `collections.OrderedDict`.


### dump and dumps

```python
def dump(obj: Any, encoded_type: Any, ...):
    ...

def dumps(obj: Any, encoded_type: Any, ...):
    ...
````

The functions `dump` and `dumps` of `typing_json` mimic the functions `dump` and `dumps` of the standard `json` library, first performing a conversion of `obj` from json-encodable type `encoded_type` to a json object before dumping.


## decoding

### from_json_obj

```python
def from_json_obj(obj: Any, t: Any) -> Any:
    ...
````

The function `to_json_obj(obj, t)` takes an object `obj` and a json encodable type `t` and converts `obj` into an equivalent object of type `t`. The conversion goes as follows:

- if `t in (bool, int, float, str)`, `obj` is returned unaltered (`TypeError` is raised if `not isinstance(obj, t)`);
- if `t in (None, NoneType)`, `None` is returned (`TypeError` is raised if `obj is not None`);
- if `t is ...`, `...` is returned (`TypeError` is raised if `obj is not None`);
- if `is_namedtuple(t)`, the key values of the (ordered) dictionary `obj` are recursively converted to the types of the fields of `t` with the same keys and any missing key is replaced with it default value in `t`, if present (`TypeError` is raised if `obj` is not a (ordered) dictionary, if `obj` contains keys which are not fields of `t`, or if a non-default field of `t` does not appear as a key in `obj`);
- if `t` is `Union[_T1,..._TN]` then conversion of `obj` to each type `_Tj` listed in the union is attempted in order and the first successful result is returned (`TypeError` is raised if no conversion is successful);
- if `t` is `Literal` then `obj` is returned unaltered (`TypeError` is raised if `not is_instance(obj, t)`);
- if `t` is `List[_T]` then all members of `obj` are recursively converted to type `_T` and a list of the results is returned (`TypeError` is raised if `obj` is not a list);
- if `t` is `Deque[_T]` then all members of `obj` are recursively converted to type `_T` and a deque of the results is returned (`TypeError` is raised if `obj` is not a list);
- if `t` is `Set[_T]` then all members of `obj` are recursively converted to type `_T` and a set of the results is returned (`TypeError` is raised if `obj` is not a list, order preservation is not guaranteed);
- if `t` is `FrozenSet[_T]` then all members of `obj` are recursively converted to type `_T` and a frozenset of the results is returned (`TypeError` is raised if `obj` is not a list, order preservation is not guaranteed);
- if `t` is `Tuple[_T,...]` then all members of `obj` are recursively converted to type `_T` and a tuple of the results is returned (`TypeError` is raised if `obj` is not a list);
- if `t` is `Tuple[_TN,...,_TN]` then all members of `obj` are recursively converted to the respective types `_Tj` and a tuple of the results is returned (`TypeError` is raised if `obj` is not a list or if the length does not match the required length for the tuple);
- if `t` is `Dict[_S, _T]` or `Mapping[_S, _T]` then all keys and values of `obj` are recursively converted to types `_S` and `_T` respectively (if `_S` is not one of `bool`, `int`, `float`, `str`, `NoneType` or `None`, the keys are first json-parsed from strings), and a dict of the results is returned (`TypeError` is raised if `obj` is not a (ordered) dictionary);
- if `t` is `OrderedDict[_S, _T]`  then all keys and values of `obj` are recursively converted to types `_S` and `_T` respectively (if `_S` is not one of `bool`, `int`, `float`, `str`, `NoneType` or `None`, the keys are first json-parsed from strings), and an ordered dict of the results is returned (`TypeError` is raised if `obj` is not an ordered dictionary);

If `t` is not json-encodable according to `is_json_encodable(t)` then `TypeError` is raised.


### load and loads

```python
def load(fp, decoded_type: Any, ...) -> Any:
    ...

def dumps(s: str, decoded_type: Any, ...) -> Any:
    ...
````

The functions `load` and `loads` of `typing_json` mimic the functions `load` and `loads` of the standard `json` library, performing a conversion of the loaded json object to json-encodable type `decoded_type` before returning.
