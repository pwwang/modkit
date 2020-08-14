"""
A package to manage your python modules
"""

__version__ = "0.2.2"

import sys
import inspect
import fnmatch
from types import ModuleType
from importlib import util
from varname import varname, VarnameRetrievingError

MYSELF = sys.modules[__name__]

class UnimportableNameError(ImportError, AttributeError):
    """Exception when name is not importable"""

class Module(ModuleType):
    """A wapper to wrap a module"""
    def __init__(self, module, prev=None):
        """Construct
        Wrap up the current module baked from the previous module

        Args:
            module (ModuleType): Current module to wrap up
            prev (ModuleType): Previous module which current is baked from
        """
        super().__init__(module.__name__, (prev or module).__doc__)
        # keep properties in one directory to keep namespace clean
        self.__dict__['__modkit_meta__'] = self.__modkit_meta__ = dict(
            prev=prev or module,
            module=module,
            envs=(module.__modkit_meta__['envs']
                  if isinstance(module, Module)
                  else vars(module)),
            # all names available to export
            all=set(),
            # aliases for existing names
            aliases={},
            # specified exports
            exports=set(),
            # specified bans
            bans=set(),
            # specified delegates
            delegate=None,
            # specified calls
            call=None,
            # If we are in the import bootstrapping searching
            # Because this only happens once, we should cache it
            # As it is been detected in __getattr__
            searching=True,
            generation=(module.__modkit_meta__['generation'] + 1
                        if isinstance(module, Module)
                        else 1)
        )

        self.__dict__['__spec__'] = self.__spec__ = (
            self.__modkit_meta__['prev'].__spec__
        )
        self.__dict__['__package__'] = self.__package__ = (
            self.__modkit_meta__['prev'].__package__
        )
        self.__dict__['__path__'] = self.__path__ = []
        self.__dict__['__file__'] = self.__file__ = (
            self.__modkit_meta__['prev'].__file__
        )

    def __repr__(self):
        if not isinstance(self.__modkit_meta__['prev'], Module):
            return repr(self.__modkit_meta__['module']).replace(
                '<module ', '<module (modkit wrapped) '
            )
        return (f"<module '{self.__modkit_meta__['module'].__name__}' @ "
                f"{id(self)} baked (generation: "
                f"{self.__modkit_meta__['generation']}) from "
                f"'{self.__modkit_meta__['prev'].__name__}'>")

    def __dir__(self):
        """Discussion:
        Should we expose all attribute names?
        Or we just do __all__
        """
        return (list(self.__modkit_meta__['envs']) +
                list(self.__modkit_meta__['aliases']))

    @property
    def __all__(self):
        if self.__modkit_meta__['all']:
            return tuple(self.__modkit_meta__['all'])

        all_avail_exports = (set(self.__modkit_meta__['envs']) |
                             set(self.__modkit_meta__['aliases']))

        for pattern in self.__modkit_meta__['exports']:
            self.__modkit_meta__['all'] |= set(
                fnmatch.filter(all_avail_exports, pattern)
            )

        if not self.__modkit_meta__['all']:
            self.__modkit_meta__['all'] = all_avail_exports

        for pattern in self.__modkit_meta__['bans']:
            self.__modkit_meta__['all'] -= set(
                fnmatch.filter(all_avail_exports, pattern)
            )
        return tuple(self.__modkit_meta__['all'])

    def __getattr__(self, name):
        # We should skip if we are from the import searching
        # This enables `from xyz import abc`
        if self.__modkit_meta__['searching']:
            try:
                prevfile, _, _, _, _ = inspect.getframeinfo(
                    inspect.currentframe().f_back
                )
                if prevfile.startswith('<frozen importlib._bootstrap'):
                    self.__modkit_meta__['searching'] = False
                    return None
            finally:
                self.__modkit_meta__['searching'] = False

        # return the attributes that available with this class
        # if name in self.__dict__:
        #     return self.__getattribute__(name)
        for ban in self.__modkit_meta__['bans']:
            if fnmatch.fnmatch(name, ban):
                raise UnimportableNameError(f'Name banned: {name}')

        if (name not in self.__all__ and
                not callable(self.__modkit_meta__['delegate'])):
            raise UnimportableNameError(f"{self.__name__}.{name}")

        # return the attributes that immediately available in original module
        if name in self.__modkit_meta__['envs']:
            return self.__modkit_meta__['envs'][name]

        # alias
        if name in self.__modkit_meta__['aliases']:
            source = self.__modkit_meta__['aliases'][name]
            if (source not in self.__modkit_meta__['envs']
                    and not self.__modkit_meta__['delegate']):
                raise UnimportableNameError(f"Alias {name} to {source} "
                                            "is an unimportable name")

            return self.__modkit_meta__['envs'][source]

        # delegate
        if callable(self.__modkit_meta__['delegate']):
            # pylint: disable=not-callable
            return self.__modkit_meta__['delegate'](self, name)

        raise AttributeError(name) # pragma: no cover

    def __setattr__(self, name, value):
        """Allow to set/update attribute values"""
        # supposed attributes added on the fly are open
        # force __all__ to be recalculated
        self.__modkit_meta__['all'] = set()
        self.__modkit_meta__['envs'][name] = value

    def __delattr__(self, name):
        # force __all__ to be recalculated
        self.__modkit_meta__['all'] = set()
        try:
            del self.__modkit_meta__['envs'][name]
        except KeyError:
            raise AttributeError(name) from None

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    def __contains__(self, name):
        return  name in self.__all__

    def __bake__(self, new_module_name):
        """make a copy of the module"""
        spec = self.__modkit_meta__['module'].__spec__
        newmod = util.module_from_spec(spec)
        spec.loader.exec_module(newmod)
        newmod.__name__ = new_module_name
        # wrap it up
        newmod = self.__class__(newmod, self)

        newmod.__modkit_meta__['aliases'] = self.__modkit_meta__[
            'aliases'
        ].copy()
        newmod.__modkit_meta__['exports'] = set(list(
            self.__modkit_meta__['exports']
        ))
        newmod.__modkit_meta__['bans'] = set(list(
            self.__modkit_meta__['bans']
        ))
        # This will not bring environment to the new module
        #
        # newmod.__modkit_meta__['delegate'] = self.__modkit_meta__['delegate']
        # newmod.__modkit_meta__['call'] = self.__modkit_meta__['call']
        #
        # Let's use the one copied in the new module itself
        for val in newmod.__modkit_meta__['envs'].values():
            if callable(val) and hasattr(val, '_modkit_delegate'):
                newmod.__modkit_meta__['delegate'] = val
            elif callable(val) and hasattr(val, '_modkit_call'):
                newmod.__modkit_meta__['call'] = val

        # register
        sys.modules[new_module_name] = newmod

        return newmod

    def __call__(self, *args, **kwargs):
        """Open API to do somehting if `module(...)` happens"""
        if not callable(self.__modkit_meta__['call']):
            raise TypeError("No function specified for "
                            "using module as callable")

        try:
            assigned_to = varname(raise_exc=True)
        except VarnameRetrievingError:
            assigned_to = None

         # pylint: disable=not-callable
        return self.__modkit_meta__['call'](self, assigned_to, *args, **kwargs)

class Modkit:
    """The Modkit class"""
    def __new__(cls, module=None):
        """We are trying to early stop search for `import ... from ...`
        If `inspect.getmodule(inspect.stack()[3].frame)` is not the right
        module, that means it's from the search
        """
        if not module:
            module = inspect.getmodule(inspect.stack()[3].frame)
        if not module:
            return None

        inst = super(Modkit, cls).__new__(cls)
        inst.module = module
        return inst

    def __init__(self, module=None):
        """Construct
        Try to detect where modkit is imported,
        fetch that module and wrap it up
        """
        # module discovered in __new__
        # pylint: disable=access-member-before-definition
        module = self.module
        self.module = Module(module)
        sys.modules[module.__name__] = self.module

    def delegate(self, delegate_func):
        """A decorator to assign the delegate function"""
        self.module.__modkit_meta__['delegate'] = delegate_func
        # for baking modules to identify it
        delegate_func._modkit_delegate = True
        return delegate_func

    def call(self, call_func):
        """A decorator to assign the call function"""
        self.module.__modkit_meta__['call'] = call_func
        # for baking modules to identify it
        call_func._modkit_call = True
        return call_func

    def postinit(self, init_func):
        """A hook for actions after a module is initialized"""
        init_func(self.module)
        return init_func

    def ban(self, *args):
        """Set the names to ban, wildcards available"""
        self.module.__modkit_meta__['bans'] |= set(args)
        # force recalculation
        self.module.__modkit_meta__['all'] = set()

    def unban(self, *args):
        """Unban something in bans"""
        self.module.__modkit_meta__['bans'] -= set(args)
        # force recalculation
        self.module.__modkit_meta__['all'] = set()

    def export(self, *args):
        """Set the names to export, wildcards available"""
        self.module.__modkit_meta__['exports'] |= set(args)
        # force recalculation
        self.module.__modkit_meta__['all'] = set()

    def alias(self, *args, **kwargs):
        """Set the alias of existing name
        It could be 2 arguments: alias -> source
        Or a dictionary with aliases as keys and sources as values
        Or kwargs with aliases as keys and sources as values

        Examples:
            >>> modkit.alias('attr_alias', 'attr')
            >>> modkit.alias({'attr_alias': 'attr'})
            >>> modkit.alias(attr_alias='attr')
        """
        # alias => souce
        aliases = {}
        if len(args) == 2:
            aliases[args[0]] = args[1]
        elif len(args) == 1 and isinstance(args[0], dict):
            aliases = args[0]
        elif args:
            raise ValueError("Expecting a dictionary for aliases")

        for alias, source in kwargs.items():
            if alias in aliases:
                raise ValueError(f'Alias {alias} mapped to multiple source.')
            aliases[alias] = source

        self.module.__modkit_meta__['aliases'].update(aliases)
        # force recalculation
        self.module.__modkit_meta__['all'] = set()

    aliases = alias
    bans = ban
    exports = export

# Wrap myself
MYSELF_WRAPPED = Modkit(MYSELF)

@MYSELF_WRAPPED.delegate
def _myself_delegate(module, name): # pylint: disable=unused-argument
    """Delegate modkit import to MYSELF"""
    if name == 'modkit':
        # make sure we return a new
        return Modkit()
    raise UnimportableNameError(name)
