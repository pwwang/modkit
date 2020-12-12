"""modkit: Tweak your modules the way you want"""
import sys
import inspect
from copy import deepcopy
from types import ModuleType
from typing import Any, Optional

from varname import varname

__version__ = '0.3.0'
__all__ = ('install', 'bake', 'submodule')

def _get_module() -> Optional[ModuleType]:
    """Try to traverse the frames to get the module"""
    frame = None
    i = 2
    while True:
        frame = sys._getframe(i)
        i += 1
        modfile = inspect.getframeinfo(frame).filename
        if modfile.startswith('<frozen'): # pragma: no cover
            continue
        break

    return inspect.getmodule(frame)

class Module(ModuleType):
    """The module wrapper class to wrap the original module
    One can access the original module by module.__origin__
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__origin__ = None

    def _from_origin(self, module: ModuleType) -> None:
        """Update the dict from the original module"""
        self.__origin__ = module
        self.__dict__.update(module.__dict__)

    def __getitem__(self, name: Any) -> Any:
        """Allow to subscribe a module if __getitem__ is defined in the module

        Args:
            name: The name of the item

        Raises:
            TypeError: if __getitem__ is not defined in the module
        """
        if '__getitem__' not in self.__dict__:
            raise TypeError("'module' object is not subscriptable")
        return self.__dict__['__getitem__'](name)

    def __getattr__(self, name: str) -> Any:
        """Allow to getattr if __getattr__ is defined in the module

        Note: if you have submodules, module.submodule will not bypass this
        function, so you have to manually import the submodules here.

        submodule is provided to tell if a submodule is loaded successfully or
        not.

        For example:
        >>> def __getattr__(name):
        >>>     submod = submodule('sub')
        >>>     if submod:
        >>>         # if submodule is loaded successfully
        >>>         return submod
        >>>     # otherwise do the tweak
        >>>     return name.upper()

        Args:
            name: The name of the attribute

        Raises:
            AttributeError: if __getattr__ is not defined in the module
        """
        if '__getattr__' not in self.__dict__:
            raise AttributeError(
                f"module '{self.__name__}' has no attribute '{name}'"
            )
        # python3.7+ has builtin __getattr__ support
        return self.__dict__['__getattr__'](name) # pragma: no cover

    def __call__(self, *args, **kwargs) -> Any:
        """Make the module callable

        Args:
            *args: Arugments for __call__ defined in the module
            **kwargs: Keyword arguments for __call__ defined in the module

        Returns:
            Anything returned from __call__ defined in the module
        """
        if '__call__' not in self.__dict__:
            raise TypeError("'module' object is not callable")
        return self.__dict__['__call__'](*args, **kwargs)

    def __repr__(self) -> str:
        """Repr for the wrapped module"""
        return repr(self.__origin__).replace(
            repr(self.__origin__.__name__),
            repr(self.__name__)
        )[:-1] + ' (wrapped by modkit)>'

def install(name: Optional[str] = None) -> None:
    """Install the modkit to wrap up the module

    Args:
        name: The name of the module. You would like to do `install(__name__)`
            But if you are lazy, you can do `install()`. The module will
            be inferred by traversing the frames.
    """
    orig_module = sys.modules[name] if name else _get_module()

    wrapped = Module(orig_module.__name__)
    wrapped._from_origin(orig_module)
    sys.modules[orig_module.__name__] = wrapped

def bake(baked_name: Optional[str] = None,
         deep: bool = False,
         name: Optional[str] = None) -> ModuleType:
    """Bake the module

    Args:
        baked_name: The name for the baked module. If not provided, will
            be inferred by varname. For example: `m = bake()` then the new
            module name will be `m`
        deep: Whether do a deep copy of the __dict__ or not.
            Note, modules and `__builtins__` are not deep copied even when
            we do deep copy
        name: Current module name. If not provided, will traverse the frame
            to get the module.

    Returns:
        The baked module
    """
    baked_name = baked_name or varname(raise_exc=False)
    if not baked_name:
        raise ValueError('A name is required to bake a module')

    module = sys.modules[name] if name else _get_module()
    baked_module = Module(baked_name)
    if deep:
        for key, val in module.__dict__.items():
            if key == '__builtins__' or isinstance(val, ModuleType):
                continue
            baked_module.__dict__[key] = deepcopy(val)
    else:
        baked_module.__dict__.update(module.__dict__)
    # pylint: disable=attribute-defined-outside-init
    baked_module.__name__ = baked_name
    sys.modules[baked_name] = baked_module
    return baked_module

def submodule(submod_name, name=None) -> Optional[ModuleType]:
    """Try importing the submodule of current wrapped module

    Note that no ImportError will be raised if failed to import; `None` will
    be returned instead.

    Args:
        submod_name: Name of the submodule.
        name: Current module name. If not provided, will traverse the frame
            to get the module.
    """
    module = sys.modules[name] if name else _get_module()
    try:
        mod = __import__(f'{module.__name__}.{submod_name}')
    except ImportError:
        return None
    else:
        names = module.__name__.split('.') + [submod_name]
        for nam in names[1:]:
            mod = getattr(mod, nam)
        return mod
