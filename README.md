# modkit

[![Pypi](https://img.shields.io/pypi/v/modkit?style=flat-square)](https://pypi.org/project/modkit/)
[![Github](https://img.shields.io/github/tag/pwwang/modkit?style=flat-square)](https://github.com/pwwang/modkit)
[![PythonVers](https://img.shields.io/pypi/pyversions/modkit?style=flat-square)](https://pypi.org/project/modkit/)
[![Travis building](https://img.shields.io/travis/pwwang/modkit?style=flat-square)](https://travis-ci.org/pwwang/modkit)

Tweak your modules the way you want

## Install
```shell
pip install -U modkit
```

## Usage

`module.py`

```python
import modkit

a = 1
d = {}

def __getattr__(name):
    # we have this supported with python3.7+
    # but with modkit, you can do it with python3.6+
    return name.upper()

def __getitem__(name):
    return name.lower()

def __call__(name):
    return name * 2

modkit.install()
```

```python
import module

module.a # 1
module.b # B
module.d # {}
module['c'] # C
module('e') # ee
```

### Bake a module

You can make a copy of your module with modkit easilyl

`module.py`

```python
from modkit import bake


```


