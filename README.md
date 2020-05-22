# Welcome to the `typing_json` library
[![Build Status](https://api.travis-ci.com/sg495/typing-json.svg?branch=master)](https://travis-ci.com/sg495/typing-json)
[![codecov](https://codecov.io/gh/sg495/typing-json/graph/badge.svg)](https://codecov.io/gh/sg495/typing-json/)
[![Generic badge](https://img.shields.io/badge/python-3.7.4+-green.svg)](https://shields.io/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/typing-json.svg)](https://pypi.python.org/pypi/typing-json/)
[![PyPI status](https://img.shields.io/pypi/status/typing-json.svg)](https://pypi.python.org/pypi/typing-json/)
[![Generic badge](https://img.shields.io/badge/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

The `typing_json` library offers type-aware JSON encoding and decoding functionalities, on top of those offered by the builtin `json` library. The functions `dump`, `dumps`, `load` and `loads` mirror the functionality of their `json` counterparts, adding type-aware encoding/decoding and runtime type-checking of decoded objects.

Supported types include JSON basic types, `Decimal`, typed collections from the `typing` library, literal types, union types, optional types and typed namedtuples. For a full list of types, see below.
The function `is_instance` extends the functionality of the builtin `isinstance` to include all the additional types supported by this library.

The [documentation](https://sg495.github.io/typing-json/typing_json/index.html) for this library was generated with [pdoc](https://pdoc3.github.io/pdoc/).

You can install the `typing_json` library with pip:

```
pip install typing_json
```


## Main goals

There are two main drivers behind the development of the `typing_json` library:

1. Type-aware **serialisation** of data using JSON.
2. Runtime **validation** of JSON data for use with static typing.

The first goal of the `typing_json` library is to automate the serialisation of statically typed data in Python.
In a statically typed Python application (e.g. one validated using [mypy](http://mypy-lang.org/)), data is often structured using simple static types.
The `typing_json` library uses these types to automate the process of JSON serialisation and de-serialisation, ensuring that the serialised data can subsequently be de-serialised into a valid instance of the original static type, equivalent to the instance that was originally serialised.

The second goal of the `typing_json` library is to automate the validation of JSON data against existing static types.
When JSON data is loaded dynamically into a statically typed Python application, it needs to be validated to ensure that it conforms to whatever static types are being used as its specification.
The `typing_json` library uses these types to automate the validation process, i.e. to perform runtime type-checking of the JSON data against the static types.
This guarantees that data successfully de-serialised from JSON using the `load`/`loads` functions of the `typing_json` library conforms to the static type provided.


## Types supported

The following types are currently supported by the `typing_json` library:

- the JSON basic types `bool`, `int`, `float`, `str` and `NoneType` (technically `type(None)`, but `None` can be used as an alias);
- the type `Decimal` from the `decimal` builtin (cf. below for the handling of numerical types);
- the following typed collections from the `typing` builtin library, as long as all generic type arguments are themselves supported: `List`, `Tuple`, `Deque`, `Set`, `FrozenSet`;
- typed namedtuples constructed using `NamedTuple` from the builtin `typing` library, as long as all fields are of supported type;
- the following typed collections from the `typing` builtin library, as long as the generic key/value generic type arguments are themselves supported: `Dict`, `Mapping` and `OrderedDict` (see below for additional requirements on the key generic type arguments and special behaviour on JSON encoding/decoding of keys);
- enumeration types
- the `Literal` types from the `typing_extensions` library, as long as all literal are of one of the JSON basic types above;
- `Optional` and `Union` types from the `typing` builtin library, as long as all generic type arguments are themselves supported (cf. below for a caveat about `Union` types).

The following function can be used at runtime to check whether `t` is a type supported by the `typing_json` library:

```python
    def is_json_encodable(t: Any, failure_callback=None) -> bool:
        ...
```

The optional parameter `failure_callback` can be used to pass a `Callable[[str], None]` that will be used to log any error messages.
The following provides an example of usage:

```python
# Python 3.7.4
>>> from typing import Dict, List, Set, Tuple
>>> from typing_json import is_json_encodable
>>> error_log = []
>>> my_callback = lambda s: error_log.append(s)
>>> is_json_encodable(List[Dict[Set[int], int]], failure_callback=my_callback)
False
>>> error_log
['Type typing.Set[int] is not keyable.',
 'Type of keys in typing.Dict[typing.Set[int], int] is not keyable.',
 'Type of elements in typing.List[typing.Dict[typing.Set[int], int]] is not json-encodable.']
```


## Overview of encoding/decoding functions

There are three pairs of encoding/decoding functions offered by the `typing_json` library, for use in three different circumstances.

The functions `to_json_obj` / `from_json_obj` offer runtime conversion of instances of supported types to/from JSON objects.

```python
    def to_json_obj(obj: Any, t: Type, use_decimal: bool = False) -> Any:
        ...

    def from_json_obj(obj: Any, t: Type, cast_decimal: bool = True) -> Any:
        ...
```

The functions `dumps` / `loads` offer (de-)serialisation of instances of supported types to/from JSON formatted strings.

```python
def dumps(obj: Any, encoded_type: Type, **kwargs) -> str:
    ...

def loads(s: str, decoded_type: Type, cast_decimal: bool = True, **kwargs) -> Any:
    ...
```

The functions `dump` / `load` offer (de-)serialisation of instances of supported types to/from JSON formatted IO streams.

```python
def dump(obj: Any, encoded_type: Type, fp, **kwargs) -> None:
    ...

def load(fp, decoded_type: Type, cast_decimal: bool = True, **kwargs) -> Any:
    ...
```

The calls `dump(obj, t, fp)` / `dumps(obj, t)` first use `to_json_obj(obj, t)` to encode an instance `obj` of a supported type `t` into a JSON object `obj_json`, then call `json.dump(obj_json)` / `json.dumps(obj_json)` to serialise `obj_json` to a file object `fp` or string.

Conversely, the calls `load(fp, t)` / `loads(s, t)` first call `json.load(fp)` / `json.loads(s)` to deserialise a JSON object `obj_json` from a file object `fp` or string `s`, then call `from_json_obj(obj_json, t)` to decode an instance `obj` of a supported type `t` from `obj_json`.

In all functions above, `TypeError` is raised if the object passed does not match the type specified.
This runtime type-checking is performed by the function `is_instance`:

```python
def is_instance(obj: Any, t: Type, failure_callback=None, cast_decimal: bool = True) -> bool:
    ...
```

The function `is_instance` extends the behaviour of the builtin `isinstance` to type-checking of instances `obj` of all types `t` supported by the `typing_json` library.
Most importantly, this includes the generic typed collections of the `typing` library, and features a slight alteration of behaviour on booleans and numerical types.


## Using `dump`, `dumps`, `load` and `loads`

The functions `dump`, `dumps`, `load` and `loads` in the `typing_json` library mirror their builtin `json` counterparts, with a couple of exceptions:

- an additional parameter `encoded_type` (resp. `decoded_type`) is used in `dump` / `dumps` (resp. in `load` / `loads`) to specify the type to be used in the JSON encoding (resp. decoding);
- an additional optional parameter `cast_decimal` (default: `True`) is used in `load` / `loads` to specify whether instances of `Decimal` (used by default to parse float literals) should be silently cast to `int` and `float` wherever the type requires them to.

Aside from the additional type parameter, the usage of `dump`, `dumps`, `load` and `loads` is the same as that of their `json` counterparts:

```python
# Python 3.7.4
>>> from typing import Dict
>>> from typing_json import load
# myexpenses.json:
#
# {
#   "home": 150.25,
#   "travel": 78.90,
#   "entertainment": 52.00
# }
#
>>> with open("myexpenses.json", "r") as fp:
...     load(fp, Dict[str, float])
...
{"home": 150.25, "travel": 78.90, "entertainment": 52.00}
```

```python
# Python 3.7.4
>>> from typing import Dict
>>> from typing_json import loads
>>> s = '{"home": 150.25, "travel": 78.9, "entertainment": 52.0}'
>>> loads(s, Dict[str, float])
{"home": 150.25, "travel": 78.90, "entertainment": 52.00}
```

```python
# Python 3.7.4
>>> from typing import Dict
>>> from typing_json import dump
>>> myexpenses = {"home": 150.25, "travel": 78.90, "entertainment": 52.00}
>>> with open("myexpenses.json", "w") as fp:
...      dump(myexpenses, Dict[str, float], fp)
...
# myexpenses.json:
#
# {
#   "home": 150.25,
#   "travel": 78.90,
#   "entertainment": 52.00
# }
#
```

```python
>>> from typing import Dict
>>> from typing_json import loads
>>> myexpenses = {"home": 150.25, "travel": 78.90, "entertainment": 52.00}
>>> dumps(myexpenses, Dict[str, float])
'{"home": 150.25, "travel": 78.9, "entertainment": 52.0}'
```




## Basic types

On JSON basic types, the `to_json_obj` and `from_json_obj` functions return their argument unchanged:

```python
# Python 3.7.4
>>> from typing_json import to_json_obj
>>> to_json_obj(True, bool)
True
>>> to_json_obj(1, int)
1
>>> to_json_obj(1.5, float)
1.5
>>> to_json_obj("hello", str)
"hello"
>>> to_json_obj(None, type(None))
None
>>> to_json_obj(None, None) # `None` is alias for `type(None)`
None
```

The exact same outcomes above are obtained if `to_json_obj` is replaced with `from_json_obj`.

The behaviour of `is_instance` on JSON basic types features two slight alterations from the behaviour of the builtin `isinstance`.
Firstly, the `bool` literals `True` and `False` are not deemed to be of type `int` by `is_instance`, but they are by the builtin `isinstance`:

```python
# Python 3.7.4
>>> from typing_json import is_instance
>>> isinstance(False, int) # builtin
True
>>> isinstance(True, int) # builtin
True
>>> is_instance(False, int) # typing_json
False
>>> is_instance(True, int) # typing_json
False
```

Secondly, instances of `int` are deemed to be of type `float` by `is_instance`, but they are not by the builtin `isinstance`:

```python
# Python 3.7.4
>>> from typing_json import is_instance
>>> isinstance(1, int) # builtin
True
>>> isinstance(1, float) # builtin
False
>>> is_instance(1, int) # typing_json
True
>>> is_instance(1, float) # typing_json
True
```


## Number types

When parsing JSON strings, from file object using `load` or from string instances using `loads`, the default behaviour is to use the constructor of class `Decimal` from the builtin `decimal` library to parse floating point literals.
This informs the following handling of number types in the `to_json_obj` / `from_json_obj` functions.

The default behaviour in `from_json_obj` is to silently decode instances of `Decimal` to instances of `int` and `float`, according to the type specified:

```python
# Python 3.7.4
>>> from decimal import Decimal
>>> from typing_json import from_json_obj
>>> from_json_obj(Decimal("1.2"), Decimal)
Decimal("1.2")
>>> from_json_obj(Decimal("1.2"), float)
1.2
>>> from_json_obj(Decimal("1.0"), Decimal)
Decimal("1.0")
>>> from_json_obj(Decimal("1.0"), float)
1.0
>>> from_json_obj(Decimal("1.0"), int)
1
```

The optional parameter `cast_decimal` of `from_json_obj` (default: `True`) can be set to `False` to disable the silent conversion of `Decimal` to `float` and `int`:

```python
# Python 3.7.4
>>> from decimal import Decimal
>>> from typing_json import from_json_obj
>>> from_json_obj(Decimal("1.2"), Decimal, cast_decimal=False)
Decimal("1.2")
>>> from_json_obj(Decimal("1.2"), float, cast_decimal=False)
# TypeError: Object Decimal('1.2') is not of json basic type t=<class 'float'>.
>>> from_json_obj(Decimal("1.0"), Decimal, cast_decimal=False)
Decimal("1.0")
>>> from_json_obj(Decimal("1.0"), float, cast_decimal=False)
# TypeError: Object Decimal('1.0') is not of json basic type t=<class 'float'>.
>>> from_json_obj(Decimal("1.0"), int, cast_decimal=False)
# TypeError: Object Decimal('1.0') is not of json basic type t=<class 'int'>.
```

To ensure that decimal precision is maintained, instances `Decimal` are always encoded into JSON as strings:

```python
# Python 3.7.4
>>> from decimal import Decimal
>>> from typing_json import to_json_obj
>>> to_json_obj(Decimal("1.2"), Decimal)
"1.2"
>>> to_json_obj(Decimal("-16"), Decimal)
"-16"
```

The optional parameter `use_decimal` of `to_json_obj` (default: `True`) can be set to `True` to instead allow instances of `Decimal` to be used directly in JSON objects:

```python
# Python 3.7.4
>>> from decimal import Decimal
>>> from typing_json import to_json_obj
>>> to_json_obj(Decimal("1.2"), Decimal, use_decimal=True)
Decimal("1.2")
>>> to_json_obj(Decimal("-16"), Decimal, use_decimal=True)
Decimal("-16")
```

Finally, integers are always silently converted to floating point numbers in `from_json_obj`, but trying to convert floating point numbers to integers will always raise an error, regardless of whether the encoded number is an integer:

```python
# Python 3.7.4
>>> from decimal import Decimal
>>> from typing_json import from_json_obj
>>> from_json_obj(1, int)
1
>>> from_json_obj(1, float)
1.0
>>> from_json_obj(1.0, float)
1.0
>>> from_json_obj(1.0, int)
# TypeError: Object 1.0 is not of json basic type t=<class 'int'>.
```


## Sequences

Instances of `List`, `Tuple` and `Deque` are encoded by `to_json_obj` as JSON lists, with their elements recursively encoded:

```python
# Python 3.7.4
>>> from collections import deque
>>> from decimal import Decimal
>>> from typing import Deque, List, Tuple
>>> from typing_json import to_json_obj
>>> to_json_obj([1, 2, 3], List[int])
[1, 2, 3]
>>> to_json_obj((1, 2.5, Decimal("3.5")), Tuple[int, float, Decimal])
[1, 2.5, "3.5"]
>>> to_json_obj(deque(["a", "b", "c"]), Deque[str])
["a", "b", "c"]
>>> to_json_obj(((0, Decimal("0.5")), (1, Decimal("3"))), Tuple[Tuple[int, Decimal], ...])
[[0, "0.5"], [1, "3"]]
```

JSON lists are are decoded by `from_json_obj` to instances of `List`, `Tuple` and `Deque` depending on the specified type, with elements recursively decoded from the elements of the JSON list:

```python
# Python 3.7.4
>>> from collections import deque
>>> from decimal import Decimal
>>> from typing import Deque, List, Tuple
>>> from typing_json import from_json_obj
>>> from_json_obj([1, 2, 3], List[int])
[1, 2, 3]
>>> from_json_obj([1, 2.5, '3.5'], Tuple[int, float, Decimal])
(1, 2.5, Decimal("3.5"))
>>> from_json_obj(["a", "b", "c"], Deque[str])
deque(["a", "b", "c"])
>>> from_json_obj([[0, "0.5"], [1, "3"]], Tuple[Tuple[int, Decimal], ...])
((0, Decimal("0.5")), (1, Decimal("3")))
```


## Sets

Instances of `Set` and `FrozenSet` are encoded by `to_json_obj` as JSON lists, with their elements recursively encoded:

```python
# Python 3.7.4
>>> from decimal import Decimal
>>> from typing import FrozenSet, Set
>>> from typing_json import to_json_obj
>>> to_json_obj({1, 2, 3}, Set[int])
[1, 2, 3]
>>> to_json_obj(frozenset({Decimal("1.5"), Decimal("2.5")}), FrozenSet[Decimal])
["1.5", "2.5"]
```

JSON lists are are decoded by `from_json_obj` to instances of `Set` and `FrozenSet` depending on the specified type, with elements recursively decoded from the elements of the JSON list:

```python
# Python 3.7.4
>>> from decimal import Decimal
>>> from typing import FrozenSet, Set
>>> from typing_json import from_json_obj
>>> from_json_obj([1, 2, 3], Set[int])
{1, 2, 3}
>>> from_json_obj(["1.5", "2.5"], FrozenSet[Decimal])
frozenset({Decimal("1.5"), Decimal("2.5")})
```


## NamedTuples

Instances of typed namedtuples constructed with `NamedTuple` are encoded by `to_json_obj` as JSON dictionaries (ordered), with the field names as their keys and the field values recursively encoded:

```python
# Python 3.7.4
>>> from collections import OrderedDict
>>> from typing import NamedTuple, Set, Tuple
>>> from typing_json import to_json_obj
>>> class Network(NamedTuple):
...     nodes: Set[int]
...     edges: Set[Tuple[int, int]]
...
>>> network = Network({0, 1, 2}, {(0, 1), (1, 2), (0, 2)})
>>> to_json_obj(network, Network)
OrderedDict([('nodes', [0, 1, 2]), ('edges', [[0, 1], [0, 2], [1, 2]])])
>>> dict(to_json_obj(network, Network))
{'nodes': [0, 1, 2], 'edges': [[0, 1], [0, 2], [1, 2]]}
```

JSON dictionaries are decoded by `from_json_obj` to instances of typed namedtuples depending on the specified type, with fields values recursively decoded from the values of the dictionary:

```python
# Python 3.7.4
>>> from typing import NamedTuple, Set, Tuple
>>> from typing_json import from_json_obj
>>> class Network(NamedTuple):
...     nodes: Set[int]
...     edges: Set[Tuple[int, int]]
...
>>> from_json_obj({'nodes': [0, 1, 2], 'edges': [[0, 1], [0, 2], [1, 2]]}, Network)
Network(nodes={0, 1, 2}, edges={(0, 1), (0, 2), (1, 2)})
```

While `collections.OrderedDict` is always used by `to_json_obj` when encoding typed namedtuples, but `from_json_obj` will also accept ordinary dictionaries (because the order of fields is already determined by the namedtuple type).
If the namedtuple has fields with default values, `from_json_obj` will use the default value for any field not appearing in the dictionary:

```python
# Python 3.7.4
>>> from typing import NamedTuple, Set, Tuple
>>> from typing_json import from_json_obj
>>> class Employee(NamedTuple):
...     name: str
...     id: int = 3
...
>>> from_json_obj({"name": "Gill", "id": 2}, Employee)
Employee(name='Gill', id=2) # "id" value from dictionary
>>> from_json_obj({"name": "John"}, Employee)
Employee(name='John', id=3) # default "id" value from `Employee`
>>> from_json_obj({"id": 0}, Employee)
# TypeError: Object {'id': 0} does not have the required keys:
# t=<class '__main__.Employee'>, missing keys {'name'}.
```

If a field in the namedtuple does not have a default value and does not appear in the dictionary, `from_json_obj` will raise `TypeError`.


## Dictionaries

Instances of `Mapping` and `Dict` are encoded by `to_json_obj` as JSON dictionaries, with their keys and values recursively encoded and their keys stringified if necessary (cf. below).
Instances of `OrderedDict` follow the exact same rules, but are encoded as instances of `collections.OrderedDict` rather than instances of `dict`.

```python
# Python 3.7.4
>>> import collections
>>> from decimal import Decimal
>>> import typing
>>> from typing import Dict, Mapping, Tuple
>>> from typing_json import to_json_obj
>>> vect = {"x": (Decimal("1.0"), Decimal("0.0")), "y": (Decimal("0.0"), Decimal("1.0"))}
>>> to_json_obj(vect, Dict[str, Tuple[Decimal, Decimal]])
{"x": ["1.0", "0.0"], "y": ["0.0", "1.0"]}
>>> to_json_obj(vect, Mapping[str, Tuple[Decimal, Decimal]])
{"x": ["1.0", "0.0"], "y": ["0.0", "1.0"]}
>>> to_json_obj(collections.OrderedDict(vect),
...             typing.OrderedDict[str, Tuple[Decimal, Decimal]])
OrderedDict([("x", ["1.0", "0.0"]), ("y", ["0.0", "1.0"])])
```

Keys are either encoded or encoded and then stringified, depending on the key type:

- JSON basic types (`bool`, `int`, `float`, `str` and `type(None)`) are encoded but not stringified;
- literal types are encoded but not stringified (because only JSON basic types are allowed as literals);
- enumeration types are encoded but not stringified (because they are already encoded as strings);
- all other types are first encoded and then stringified.

For example, dictionaries using tuples as keys have their keys first encoded into lists and then stringified to form the keys of the final JSON dictionary:

```python
# Python 3.7.4
>>> from typing import Dict, Tuple
>>> from typing_json import to_json_obj
>>> to_json_obj({(0,1): "yes", (2,3): "no"}, Dict[Tuple[int, int], str])
{'[0, 1]': 'yes', '[2, 3]': 'no'}
```

JSON dictionaries are decoded by `from_json_obj` to instances of `Dict` and `Mapping` depending on the specified type. JSON ordered dictionaries (`collections.OrderedDict`) are decoded by `from_json_obj` to instances of `Dict`, `Mapping` and `OrderedDict` depending on the specified type.
Values and keys are recursively decoded, and keys are first de-serialised from strings (using `json.loads`) if they were stringified as part of the encoding.

```python
# Python 3.7.4
>>> import collections
>>> from decimal import Decimal
>>> import typing
>>> from typing import Dict, Mapping, Tuple
>>> from typing_json import from_json_obj
>>> vect_json = {"x": ["1.0", "0.0"], "y": ["0.0", "1.0"]}
>>> from_json_obj(vect_json, Dict[str, Tuple[Decimal, Decimal]])
{"x": (Decimal("1.0"), Decimal("0.0")), "y": (Decimal("0.0"), Decimal("1.0"))}
>>> from_json_obj(vect_json, Mapping[str, Tuple[Decimal, Decimal]])
{"x": (Decimal("1.0"), Decimal("0.0")), "y": (Decimal("0.0"), Decimal("1.0"))}
>>> from_json_obj(collections.OrderedDict(vect_json),
...               typing.OrderedDict[str, Tuple[Decimal, Decimal]])
OrderedDict([("x", (Decimal("1.0"), Decimal("0.0"))), ("y", (Decimal("0.0"), Decimal("1.0")))])
>>> from_json_obj({'[0, 1]': 'yes', '[2, 3]': 'no'}, Dict[Tuple[int, int], str])
{(0,1): "yes", (2,3): "no"}
```


## Enumerations

Enumerations members are encoded by using the corresponding member names and decoded by associating the number to the member of corresponding name:

```python
# Python 3.7.4
>>> from enum import Enum
>>> from typing_json import to_json_obj, from_json_obj
>>> class Color(Enum):
...     RED = (1.0, 0.0, 0.0)
...     GREEN = (0.0, 1.0, 0.0)
...     BLUE = (0.0, 0.0, 1.0)
...
>>> to_json_obj(Color.RED, Color)
"RED"
>>> from_json_obj("RED", Color)
<Color.RED: (1.0, 0.0, 0.0)>
>>> to_json_obj({Color.RED: (255, 0, 0),
...              Color.GREEN: (0, 255, 0),
...              Color.BLUE: (0, 0, 255)},
...             Dict[Color, Tuple[int, int, int]])
{'RED': [255, 0, 0], 'GREEN': [0, 255, 0], 'BLUE': [0, 0, 255]}
```



## Literal types

Literal types can be constructed using `typing_extensions.Literal`, as long as the literals are all of JSON basic type.
Literal types are encoded/decoded exactly like JSON basic types would, i.e. nothing is done to them.


## Optional types

When encoding instances of an `Optional` type, it is first checked whether the instance can be encoded using the given generic type argument. If not, it is checked that the instance is `None`, in which case `None` is returned as the encoding (following the procedure for the JSON basic type `type(None)`).

```python
# Python 3.7.4
>>> from typing import Dict, Optional, Set
>>> from typing_json import to_json_obj
>>> to_json_obj({"set": {1, 2, 3}}, Dict[str, Optional[Set[int]]])
{"set": [1, 2, 3]}
>>> to_json_obj({"set": None}, Dict[str, Optional[Set[int]]])
{"set": None}
```

Similarly, when decoding instances of an `Optional` type, it is first checked whether the JSON object can be decoded using the given generic type argument. If not, it is checked that the instance is `None`, in which case `None` is returned as the decoding.

```python
# Python 3.7.4
>>> from typing import Dict, Optional, Set
>>> from typing_json import from_json_obj
>>> from_json_obj({"set": [1, 2, 3]}, Dict[str, Optional[Set[int]]])
{"set": {1, 2, 3}}
>>> from_json_obj({"set": None}, Dict[str, Optional[Set[int]]])
{"set": None}
```

## Union types

When serialising instances `obj` of a `Union` type, the generic type arguments of `Union` are tried in sequence until a type `T` is found of which `obj` is an instance (accoring to the `is_instance` function).
The serialisation then proceeds using `T` as the static type:

```python
# Python 3.7.4
>>> from typing import Union
>>> from typing_json import dumps
>>> dumps(1, Union[int, str, float]) # same as `dumps(1, int)`
'1'
>>> dumps("hello", Union[int, str, float]) # same as `dumps("hello", str)`
'"hello"'
>>> dumps(2.5, Union[int, str, float]) # same as `dumps(2.5, float)`
'2.5'
```

When the JSON data `obj_json` is de-serialised, the generic type arugments of `Union` ara again tried in sequence until a type `T` is found which results in correct de-serialisation of `obj_json`:

```python
# Python 3.7.4
>>> from typing import Union
>>> from typing_json import loads
>>> loads('1', Union[int, str, float]) # same as `loads(1, int)`
1
>>> loads('"hello"', Union[int, str, float]) # same as `loads("hello", str)`
"hello"
>>> loads('2.5', Union[int, str, float]) # same as `loads(2.5, float)`
2.5
```

This works well as long as the JSON encodings of the types are disjoint, as is the case for all JSON basic types.
Unfortunately, some issues arise with overlapping union types, explained more in detail below.
In short: if two types in a `Union` have overlapping JSON encodings (e.g. `List` and `Set` are both encoded into JSON using lists), they may be deserialised to the incorrect runtime type (though the static `Union` type will still be respected).

```python
# Python 3.7.4
>>> from typing import List, Set, Union
>>> from typing_json import dumps, loads
>>> UnionT = Union[List[int], Set[int]]
>>> dumps([1, 2, 3], UnionT)
'[1, 2, 3]'
>>> dumps({1, 2, 3}, UnionT)
'[1, 2, 3]'
>>> loads(dumps([1, 2, 3], UnionT), UnionT)
[1, 2, 3]
>>> loads(dumps({1, 2, 3}, UnionT), UnionT)
[1, 2, 3]
```

Tagged unions can be used to mitigate this issue. Currently, tagged unions need to be defined manually (cf. below), but an automated way to construct them is a planned feature for future versions.


## Overlapping union types

However, this may create some issues when the following conditions are met:

1. the JSON encodings for two type in the `Union` overlap, as is the case for the collections `List`, `Tuple`, `Deque`, `Set` and `FrozenSet`;
2. the application depends on the runtime type of the `Union` instances in a way which results in incompatible behaviour on the overlaps.

The de-serialised object is still going to be a valid instance of the `Union` type, but its runtime type may not be the expected one.
To see a concrete example of this, imagine that we have a network with nodes labelled by `int`, featuring both directed and undirected edges.
The directed edges are encoded as 2-tuples, while the undirected edges are encoded as frozensets with two elements.
Let's look at what happens when we serialise and de-serialise such a network:

```python
# Python 3.7.4
>>> from typing import FrozenSet, NamedTuple, Set, Tuple, Union
>>> from typing_json import dumps, loads
>>> class Network(NamedTuple):
...     nodes: Set[int]
...     edges: Set[Union[Tuple[int, int], FrozenSet[int]]]
...
>>> nodes = {1, 2, 3}
>>> edges = {(1, 2), frozenset({2, 3}), frozenset({1, 3})}
>>> network = Network(nodes, edges)
>>> print(network)
Network(nodes={1, 2, 3}, edges={(1, 2), frozenset({1, 3}), frozenset({2, 3})})
>>> network_serialised = dumps(network, Network)
>>> print(network_serialised)
{"nodes": [1, 2, 3], "edges": [[1, 2], [1, 3], [2, 3]]}
>>> network_deserialised = loads(network_serialised, Network)
>>> print(network_deserialised)
Network(nodes={1, 2, 3}, edges={(1, 2), (1, 3), (2, 3)})
```

Both directed edges (instances of `Tuple[int, int]`) and undirected edges (instances of `FrozenSet[int]` with two elements) in our `Network` data structure are encoded as lists with two elements.
For example, `[1, 3]` is the encoding of both the undirected edge `frozenset({1, 3})` (which is in our network) and a directed edge `(1, 3)` (which is not in our network).
Because of this, `[1, 3]` can be deserialised using both `Tuple[int, int]` and `FrozenSet[int]`: since `Tuple[int, int]` appears first in the list of generic type arguments to `Union`, `[1, 3]` will be deserialised to a directed edge `(1, 3)`, even though it was serialised from an undirected edge `frozenset({1, 3})`.
Indeed, you can see from the prints of the example above that our original network had one directed edge `(1, 2)` and two undirected edges `frozenset({1, 3})` and `frozenset({2, 3})`, while the network we de-serialised has three directed edges `(1, 2)`, `(1, 2)` and `(2, 3)` and no undirected edges.

A way to solve this issue is to use a tagged union instead of the original union:

```python
# Python 3.7.4
>>> from typing import FrozenSet, NamedTuple, Set, Tuple, Union
>>> from typing_extensions import Literal
>>> from typing_json import dumps, loads
>>> DirEdgeT = Tuple[Literal["d"], Tuple[int, int]]
>>> UndirEdgeT = Tuple[Literal["u"], FrozenSet[int]]
>>> class Network(NamedTuple):
...     nodes: Set[int]
...     edges: Set[Union[DirEdgeT, UndirEdgeT]]
...     @staticmethod
...     def from_untagged(nodes: Set[int],
...                       edges: Set[Union[Tuple[int, int], FrozenSet[int]]]) -> Network:
...         tagged_edges = {("d", e) if isinstance(e, tuple) else ("u", e) for e in edges}
...         return Network(nodes, tagged_edges)
...
```

The factory method `from_untagged` is there to allow automated tagging of edges as directed/undirected based on their runtime type: it is not used when de-serialising the network objects from JSON.
Because the union is tagged, the edges are now de-serialised to the correct runtime type:

```python
# Python 3.7.4
>>> nodes = {1, 2, 3}
>>> edges = {(1, 2), frozenset({2, 3}), frozenset({1, 3})}
>>> network = Network.from_untagged(nodes, edges)
>>> print(network)
Network(nodes={1, 2, 3},
        edges={('u', frozenset({1, 3})), ('u', frozenset({2, 3})), ('d', (1, 2))})
>>> network_serialised = dumps(network, Network)
>>> print(network_serialised)
{"nodes": [1, 2, 3], "edges": [["u", [1, 3]], ["u", [2, 3]], ["d", [1, 2]]]}
>>> network_deserialised = loads(network_serialised, Network)
>>> print(network_deserialised)
Network(nodes={1, 2, 3},
        edges={('u', frozenset({1, 3})), ('u', frozenset({2, 3})), ('d', (1, 2))})
```
