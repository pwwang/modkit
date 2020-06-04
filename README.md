# modkit

[![Pypi](https://img.shields.io/pypi/v/modkit?style=flat-square)](https://pypi.org/project/modkit/)
[![Github](https://img.shields.io/github/tag/pwwang/modkit?style=flat-square)](https://github.com/pwwang/modkit)
[![PythonVers](https://img.shields.io/pypi/pyversions/modkit?style=flat-square)](https://pypi.org/project/modkit/)
[![Travis building](https://img.shields.io/travis/pwwang/modkit?style=flat-square)](https://travis-ci.org/pwwang/modkit)

A package to manage your python modules

## Install
```shell
pip install modkit
```

## Usage

### Allowing specific names to be imported, even with `from ... import *`
`mymodule.py`:
```python
from modkit import modkit
modkit.exports('a', 'b')
# Now you can specify glob patterns for exports via 0.1.0
# modkit.exports('p*') # works with dynamic exports
a = 1
b = 2
c = 3
```

Try to import this module:
```python
import mymodule as mm
mm.a # 1
mm.b # 2
mm.c # NameNotImportable
```

```python
from mymodule import *
a # 1
b # 2
c # NameError

# NameNotImportable
from mymodule import c
```

### Banning certain names
`mymodule.py`:
```python
from modkit import modkit
modkit.ban('a')
a = 1
```

```python
import mymodule as mm
mm.a # UnimportableNameError

# UnimportableNameError
from mymodule import a
```

### Aliasing names
`mymodule.py`:
```python
from modkit import modkit

modkit.alias('some_internal_wired_name', 'a')
some_internal_wired_name = 1
```

```python
from mymodule import a
a # 1
```

### Importing names dynamically
`mymodule.py`:
```python
from modkit import modkit

@modkit.delegate
def delegate(name):
    if name == 'a':
        return 1
    if name == 'b':
        return 2
    if name == 'c':
        return lambda: 3

```

```python
from mymodule import a, b, c
a # 1
b # 2
c() # 3

```

> NOTE: since `0.2.0`, you have to use `decorator` `modkit.delegate` for delegator \
>       `_modkit_delegate` is not available any more \
>       Same for `_modkit_call`, do `@modkit.call` as well

### Using model as a function
`mymodule.py`
```python
from modkit import modkit

@modkit.call
def call(module, assigned_to, value):
    print(f'Value {value} is assigned to: {assigned_to or 'nothing'}')
    return value

# module and assigned_to are required arguments
# you can pass other arbitrary arguments other than value
```

```python
import mymodule

result = mymodule(1)
# Value 1 is assigned to: result
# result == 1

mymodule(10)
# Value 10 is assigned to: nothing
```

### Baking a module
`mymodule.py`
```python
from modkit import modkit

data = {}

@modkit.call
def call(module, assigned_to):
    # module is deeply baked!
    newmod = module.__bake__(assigned_to)
    return newmod
```

```python
import mymodule
mymodule2 = mymodule()
mymodule2.data['a'] = 1

# mymodule.data == {}
```

### Submodule
`submodule.py`
```python
data = {}
```

`mymodule.py`
```python
from modkit import modkit
from .submodule import data

@modkit.call
def call(module, assigned_to):
    newmod = module.__bake__(assigned_to)
    return newmod
```

```python
import mymodule
mymodule2 = mymodule()
mymodule2.data['a'] = 1

# mymodule2.data == mymodule.data ==  {'a': 1}
```
