__version__ = "0.0.8"

import sys
import ast
import inspect
import fnmatch
from types import ModuleType
from importlib import util


class NameBannedFromImport(ImportError): pass
class NameNotImportable(ImportError): pass
class NameNotExists(ImportError): pass

class Module(ModuleType):

	def __init__(self, module, base = None):
		super(Module, self).__init__(module.__name__)
		# keep properties in one directory to keep namespace clean
		self._mkmeta = dict(
			base        = base or module,
			module      = module,
			envs        = module._mkenvs if isinstance(module, Module) else vars(module),
			exports     = set(),
			wildexports = set(),
			banned      = {'modkit', 'Modkit', '_modkit_delegate'},
			alias       = {}
		)
		self.__doc__ = self._mkmeta['base'].__doc__

		self._mkenvs['__path__'] = []
		self._mkenvs['__file__'] = self._mkmeta['base'].__file__

	def __repr__(self):
		if self._mkmeta['module'] is self._mkmeta['base']:
			return repr(self._mkmeta['module']).replace('<module ', '<module (modkit wrapped) ')
		return "<module '%s' @ %s baked from '%s'>" % (
			self._mkmeta['module'].__name__, id(self), self._mkmeta['base'].__name__)

	@property
	def _mkbase(self):
		return self._mkmeta['base']._mkbase \
			if isinstance(self._mkmeta['base'], Module) \
			else self._mkmeta['base']

	@property
	def _mkenvs(self):
		return self._mkmeta['envs']

	@property
	def _mkexports(self):
		return self._mkmeta['exports']

	@property
	def _mkwildexports(self):
		return self._mkmeta['wildexports']

	@property
	def _mkbanned(self):
		return self._mkmeta['banned']

	@property
	def _mkalias(self):
		return self._mkmeta['alias']

	def __getattr__(self, name):
		if name == '__all__':
			allexports = set(self._mkenvs.keys())
			exports    = set()
			for pattern in self._mkwildexports:
				exports |= set(fnmatch.filter(allexports, pattern))
			exports |= self._mkexports
			return list((exports or allexports) - self._mkbanned)

		rname = self._mkalias.get(name, name)
		if name in self._mkbanned or rname in self._mkbanned:
			raise NameBannedFromImport('{}.{}'.format(self.__name__, name))

		if name in ('__path__', '__file__'):
			# should not be banned
			return self._mkenvs[name]

		if not self._mkexports and not self._mkwildexports:
			pass
		elif self._mkexports and (name in self._mkexports or rname in self._mkexports):
			pass
		elif self._mkwildexports and any(fnmatch.filter([name, rname], pattern) \
			for pattern in self._mkwildexports):
			pass
		else:
			raise NameNotImportable('{}.{}'.format(self.__name__, name))

		if name in self._mkenvs or rname in self._mkenvs:
			return self._mkenvs[rname]

		if '_modkit_delegate' in self._mkenvs and callable(self._mkenvs['_modkit_delegate']):
			return self._mkenvs['_modkit_delegate'](name)
		raise AttributeError # pragma: no cover

	def __call__(self, *args, **kwargs):

		try:
			parent = inspect.stack()[1]
			code   = parent[4][0].strip()
			parsed = ast.parse(code)
			# new module name
			nmname = parsed.body[0].targets[0].id
		except AttributeError: # pragma: no cover
			nmname = self.__name__ + '_baked'

		#sys.modules.pop(nmname, None)
		# make a copy of the module
		spec = self._mkbase.__spec__
		newmod = util.module_from_spec(spec)
		spec.loader.exec_module(newmod)
		newmod.__name__ = nmname
		newmod = self.__class__(newmod, self._mkbase)
		sys.modules[nmname] = newmod

		if '_modkit_call' in self._mkenvs and callable(self._modkit_call):
			self._modkit_call(self._mkmeta['module'], newmod, *args, **kwargs)

		return newmod

class Modkit(object):

	def __init__(self):
		# whereever imports this module directly

		frame = None
		for f in inspect.getouterframes(inspect.currentframe())[1:]:
			if f[0].f_code.co_filename.startswith('<frozen importlib'): # pragma: no cover
				continue
			frame = f[0]
			break

		modname = frame.f_locals['__name__']
		if modname == '__main__': # pragma: no cover
			raise ImportError('modkit is intended to be used in a module other than a script.')

		module = sys.modules[modname] if modname in sys.modules else inspect.getmodule(frame)
		if isinstance(module, Module):
			self.module = module
		else:
			self.module = Module(module)
			sys.modules[module.__name__] = self.module

	def exports(self, *names):
		for name in names:
			if '*' in name or '?' in name or '[' in name:
				self.module._mkwildexports.add(name)
			else:
				self.module._mkexports.add(name)
		return self

	export = exports

	def ban(self, *names):
		self.module._mkmeta['banned'] |= set(names)
		return self

	def unban(self, *names):
		self.module._mkmeta['banned'] -= set(names)
		return self

	def alias(self, frm, to):
		self.module._mkalias[to] = frm
		return self

	def delegate(self, func):
		if not callable(func): # pragma: no cover
			raise TypeError('modkit delegate requires a callable.')
		self.module._mkenvs['_modkit_delegate'] = func
		return self

	def call(self, func): # pragma: no cover
		if not callable(func):
			raise TypeError('modkit call requires a callable.')
		self.module._mkenvs['_modkit_call'] = func
		return self
