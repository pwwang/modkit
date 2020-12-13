import pytest

from types import ModuleType

def test_raw():
    from . import raw_module
    with pytest.raises(AttributeError):
        raw_module.x

    with pytest.raises(TypeError):
        raw_module[1]

    with pytest.raises(TypeError):
        raw_module(1)


def test_bare_wrapped():
    from . import bare_wrapped_module
    with pytest.raises(AttributeError, match="has no attribute 'x'"):
        bare_wrapped_module.x

    with pytest.raises(TypeError, match="not subscriptable"):
        bare_wrapped_module[1]

    with pytest.raises(TypeError, match="object is not callable"):
        bare_wrapped_module(1)

    assert 'wrapped by modkit' in repr(bare_wrapped_module)


def test_wrapped():
    from . import wrapped_module

    assert wrapped_module.y == 'Y'
    assert wrapped_module['X'] == 'x'

    baked = wrapped_module('baked')
    assert baked.__name__ == 'baked'
    assert 'wrapped by modkit' in repr(baked)
    assert baked.d == {}
    baked.d['a'] = 2
    assert baked.d['a'] == 2
    assert wrapped_module.d == {}

    with pytest.raises(ValueError, match='A name is required'):
        wrapped_module(None)

    import baked as baked2
    assert baked2 is baked

def test_with_submodule():
    from . import with_submodules
    assert isinstance(with_submodules.sub, ModuleType)

    assert with_submodules.x == 'X'

    from .with_submodules import sub
    assert sub.s == 1

    baked_ws = with_submodules('baked_ws')
    from baked_ws import sub as sub2
    assert sub2 is sub
