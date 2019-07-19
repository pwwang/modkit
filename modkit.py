__version__ = '0.0.7'

import sys
import ast
import inspect
from types import ModuleType
from importlib import util


class NameBannedFromImport(ImportError): pass
class NameNotImportable(ImportError): pass
class NameNotExists(ImportError): pass

class Module(ModuleType):

	def __init__(self, module, basemodule = None):
		super(Module, self).__init__(module.__name__)
		self.__basemodule = basemodule or module
		self.__module = module
		self.__envs   = module._envs if isinstance(module, Module) else vars(module)
		self.__envs['__path__'] = []
		self.__envs['__file__'] = self.__basemodule.__file__
		self.__doc__ = self.__basemodule.__doc__

		self.__exports = set()
		self.__banned  = set(['modkit', 'Modkit', '_modkit_delegate'])
		self.__alias   = {}

	def __repr__(self):
		if self.__module is self.__basemodule:
			return repr(self.__module).replace('<module ', '<module (modkit wrapped) ')
		return "<module '%s' @ %s baked from '%s'>" % (
			self.__module.__name__, id(self), self.__basemodule.__name__)

	@property
	def _basemodule(self):
		return self.__basemodule._basemodule if isinstance(self.__basemodule, Module) \
			else self.__basemodule

	def __getattr__(self, name):
		if name == '__all__':
			exports = self.__exports or set(self.__envs.keys())
			return list(exports - self.__banned)


		if name == '_exports':
			return self.__exports
		if name == '_banned':
			return self.__banned
		if name == '_alias':
			return self.__alias
		if name == '_envs':
			return self.__envs

		rname = self.__alias.get(name, name)
		if name in self.__banned or rname in self.__banned:
			raise NameBannedFromImport('{}.{}'.format(self.__name__, name))

		if name in ('__path__', '__file__'):
			# should not be banned
			return self.__envs[name]

		if self.__exports and name not in self.__exports and rname not in self.__exports:
			raise NameNotImportable('{}.{}'.format(self.__name__, name))

		if name in self.__envs or rname in self.__envs:
			return self.__envs[rname]

		if '_modkit_delegate' in self.__envs and callable(self.__envs['_modkit_delegate']):
			return self.__envs['_modkit_delegate'](name)
		raise AttributeError

	def __call__(self, *args, **kwargs):

		try:
			parent = inspect.stack()[1]
			code   = parent[4][0].strip()
			parsed = ast.parse(code)
			# new module name
			nmname = parsed.body[0].targets[0].id
		except AttributeError:
			nmname = self.__name__ + '_baked'

		#sys.modules.pop(nmname, None)
		# make a copy of the module
		spec = self._basemodule.__spec__
		newmod = util.module_from_spec(spec)
		spec.loader.exec_module(newmod)
		newmod.__name__ = nmname
		newmod = self.__class__(newmod, self._basemodule)
		sys.modules[nmname] = newmod

		if '_modkit_call' in self.__envs and callable(self._modkit_call):
			self._modkit_call(self.__module, newmod, *args, **kwargs)

		return newmod

class Modkit(object):

	def __init__(self):
		# whereever imports this module directly

		frame = None
		for f in inspect.getouterframes(inspect.currentframe())[1:]:
			if f[0].f_code.co_filename.startswith('<frozen importlib'):
				continue
			frame = f[0]
			break

		modname = frame.f_locals['__name__']
		if modname == '__main__':
			raise ImportError('modkit is intended to be used in a module other than a script.')

		module = sys.modules[modname] if modname in sys.modules else inspect.getmodule(frame)
		if isinstance(module, Module):
			self.module = module
		else:
			self.module = Module(module)
			sys.modules[module.__name__] = self.module

	def exports(self, *names):
		self.module._exports |= set(names)

	def ban(self, *names):
		self.module._banned |= set(names)

	def unban(self, *names):
		self.module._banned -= set(names)

	def alias(self, frm, to):
		self.module._alias[to] = frm

	def delegate(self, func):
		if not callable(func):
			raise TypeError('modkit delegate requires a callable.')
		self.module._envs['_modkit_delegate'] = func

	def call(self, func):
		if not callable(func):
			raise TypeError('modkit call requires a callable.')
		self.module._envs['_modkit_call'] = func
