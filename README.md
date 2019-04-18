# modkit

A package to manage your python modules

## Install
```shell
# released version
pip install modkit
# latest version
pip intall git+https://github.com/pwwanbg/modkit
```

## Usage

### Allowing specific names to be imported, even with `from ... import *`
`mymodule.py`:  
```python
from modkit import Modkit
modkit = Modkit()
modkit.exports('a', 'b')
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
from modkit import Modkit
modkit = Modkit()
modkit.ban('a')
a = 1
```

```python
import mymodule as mm
mm.a # NameBannedFromImport

# NameBannedFromImport
from mymodule import a
```

### Aliasing names
`mymodule.py`:  
```python
from modkit import Modkit
modkit = Modkit()
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
from modkit import Modkit
modkit = Modkit()

def delegate(name):
	if name == 'a':
		return 1
	if name == 'b':
		return 2
	if name == 'c':
		return lambda: 3

modkit.delegate(delegate)
```

```python
from mymodule import a, b, c
a # 1
b # 2
c() # 3

# NameBannedFromImport
from mymodule import delegate

# if you want to reuse it
# mymodule.modkit.unban('delegate')
```

`modkit` has reserved delegate function with name `_modkit_delegate`. With this function defined in your module, you won't have to call `modkit.delegate`

`mymodule.py`
```python
import modkit
modkit.Modkit()

def _modkit_delegate(name):
	if name == 'a':
		return 1
	if name == 'b':
		return 2
	if name == 'c':
		return lambda: 3

# nothing needs to do
```

Then you are able to import a, b and c from mymodule:
```python
from mymodule import a, b, c
```

### Generating a new module based on current one
`mymodule.py`  
```python
import modkit
modkit.Modkit()

A = 1
def _modkit_call(module, a):
	setattr(module, 'A', 2)
	return module
```

```python
import mymodule
A # 1
mymodule2 = mymodule(2)
mymodule2.A # 2
from mymodule2 import A
A # 2
from mymodule import A
A # 1
```
