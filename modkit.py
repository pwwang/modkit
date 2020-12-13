"""modkit: Tweak your modules the way you want"""
import sys
import inspect
from copy import deepcopy
from types import ModuleType
from typing import Any, Optional
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder, Loader
from importlib.util import module_from_spec

from varname import varname

__version__ = '0.3.1'
__all__ = ('install', 'bake', 'submodule')

def _module_from_frames() -> Optional[ModuleType]:
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
    def __init__(self, name: str, doc: Optional[str] = None) -> None:
        super().__init__(name, doc)
        self.__origin__ = None

    def _exec_from(self, module: ModuleType) -> None:
        """Update the dict from the original module"""
        self.__origin__ = module
        self.__doc__ = module.__doc__
        self.__dict__.update(
            {key: val for key, val in module.__dict__.items() if key != '__name__'}
        )

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
    orig_module = sys.modules[name] if name else _module_from_frames()

    wrapped = Module(orig_module.__name__)
    wrapped._exec_from(orig_module)
    sys.modules[orig_module.__name__] = wrapped

def bake(baked_name: Optional[str] = None,
         name: Optional[str] = None) -> ModuleType:
    """Bake the module

    Args:
        baked_name: The name for the baked module. If not provided, will
            be inferred by varname. For example: `m = bake()` then the new
            module name will be `m`
        name: Current module name. If not provided, will traverse the frame
            to get the module.

    Returns:
        The baked module
    """
    baked_name = baked_name or varname(raise_exc=False)
    if not baked_name:
        raise ValueError('A name is required to bake a module')

    origin = sys.modules[name] if name else _module_from_frames()
    # get a new module
    orig_spec = origin.__spec__
    origin = module_from_spec(orig_spec)
    orig_spec.loader.exec_module(origin)

    class ModuleLoader(Loader):
        """Module loader to load the baked module"""
        def create_module(self, spec):
            """Create the module"""
            return Module(baked_name)

        def exec_module(self, module):
            """Execute the module by inheriting from the original module"""
            module._exec_from(origin)

    class ModuleFinder(MetaPathFinder):
        """Module finder to find the baked module"""
        def find_spec(self, fullname, path, target=None):
            if fullname != baked_name:
                return None
            return ModuleSpec(baked_name, ModuleLoader())

    sys.meta_path.append(ModuleFinder())
    # Now we can do import, and note this has the lowest priority
    return __import__(baked_name)

def submodule(submod_name, name=None) -> Optional[ModuleType]:
    """Try importing the submodule of current wrapped module

    Note that no ImportError will be raised if failed to import; `None` will
    be returned instead.

    Args:
        submod_name: Name of the submodule.
        name: Current module name. If not provided, will traverse the frame
            to get the module.
    """
    module = sys.modules[name] if name else _module_from_frames()
    try:
        mod = __import__(f'{module.__name__}.{submod_name}')
    except ImportError:
        return None
    else:
        names = module.__name__.split('.') + [submod_name]
        for nam in names[1:]:
            mod = getattr(mod, nam)
        return mod
