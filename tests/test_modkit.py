import sys
import pytest
# rarely used in this test, import here for wrapping test
import ast
from pathlib import Path
from subprocess import check_output
from modkit import Module, UnimportableNameError
from . import (module, module_empty, module_alias,
               submodule)
from .module import xyz

HERE = Path(__file__).parent.resolve()

def test_init():
    import modkit
    assert sys.modules['tests.module'] is module
    with pytest.raises(UnimportableNameError):
        modkit.whatever_nonexisting

def test_module_delegated():
    assert xyz == 'xyz'
    assert module.xyz == 'xyz'
    assert module.mnq == 'mnq'
    assert module.MUTABLE == {}

def test_module_baking():
    module2 = module()
    assert module.MUTABLE == module2.MUTABLE
    assert id(module.MUTABLE) != id(module2.MUTABLE)

    assert module.IMMUTABLE is module2.IMMUTABLE

    assert 'baked (generation' in repr(module2)

    module.func(1)
    module2.func(2)
    assert module.MUTABLE['a'] == 1
    assert module2.MUTABLE['a'] == 2

    module3 = module2()
    module3.func(3)
    assert module.MUTABLE['a'] == 1
    assert module2.MUTABLE['a'] == 2
    assert module3.MUTABLE['a'] == 3


def test_module_wrapping():
    module3 = Module(ast)
    assert '(modkit wrapped)' in repr(module3)

def test_dir_all():
    assert dir(module) == [
        'BANNED_NAME1', 'BANNED_NAME2', 'EXPORT_ABLE',
        'EXPORT_ABLE2', 'IMMUTABLE', 'MUTABLE', 'THIS_IS_ALSO_BANNED',
        'THIS_IS_ALSO_EXPORTABLE', '__builtins__', '__cached__', '__doc__',
        '__file__', '__loader__', '__modkit_meta__', '__name__', '__package__',
        '__path__', '__spec__', 'call', 'delegate', 'func', 'func2', 'modkit'
    ]

    assert list(sorted(module.__all__)) == [
        'EXPORT_ABLE', 'EXPORT_ABLE2', 'IMMUTABLE', 'MUTABLE',
        'THIS_IS_ALSO_EXPORTABLE', '__builtins__', '__cached__', '__doc__',
        '__file__', '__loader__', '__modkit_meta__', '__name__', '__package__',
        '__path__', '__spec__', 'call', 'delegate', 'func', 'func2', 'modkit'
    ]

def test_getattribute():
    assert 'module.py' in module.__file__
    assert isinstance(module.__modkit_meta__, dict)

def test_unimportable_names():
    with pytest.raises(UnimportableNameError):
        module.THIS_IS_ALSO_BANNED

    module.modkit.unban('THIS_IS_ALSO_BANNED')
    assert module.THIS_IS_ALSO_BANNED == 3

    with pytest.raises(UnimportableNameError):
        module_empty.BANNED_NAME1

def test_alias():
    assert module_alias.NAME1 is module_alias.NAME2
    assert module_alias.NAME3 is module_alias.NAME4
    with pytest.raises(UnimportableNameError):
        module_alias.NAME6
    with pytest.raises(UnimportableNameError):
        module_alias.NAME7

    with pytest.raises(ValueError):
        module_alias.modkit.alias(1)

def test_not_calling():
    with pytest.raises(TypeError):
        module_empty()

def test_no_assigned_to():
    with pytest.raises(ValueError):
        module()

def test_from_baked_import():
    mx1 = module()
    mx2 = mx1()
    from mx2 import MUTABLE
    assert MUTABLE == {}

def test_everything_import():
    out = check_output([
        sys.executable,
        str(HERE.joinpath('../test_import_everything/everything_test.py'))
    ])
    assert out == b'12NameError'

def test_submodule():
    # submodule should not be baked
    sub2 = submodule()
    assert sub2.NAME1 is submodule.NAME1
    assert sub2.NAME3 is submodule.NAME3

    assert sub2.sub is submodule.sub
