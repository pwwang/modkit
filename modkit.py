VERSION = '0.0.1'

import sys
import inspect
from types import ModuleType


class NameBannedFromImport(ImportError): pass
class NameNotExportable(ImportError): pass
class NameNotExists(ImportError): pass

class Module(ModuleType):

	def __init__(self, oldmod):
		self._vars = dict(
			oldmod   = oldmod,
			banned   = set(['_modkit_delegate']),
			exports  = set(),
			alias    = {},
			delegate = None
		)
	
	def __getattr__(self, name):
		if name == '__all__':
			exports = set(list(self._vars['exports']) or dir(self._vars['oldmod']))
			return list(exports - self._vars['banned'])
		if name == '__path__':
			return None

		# real name
		rname = self._vars['alias'].get(name, name)
		# check if it is banned
		if name in self._vars['banned'] or rname in self._vars['banned']:
			raise NameBannedFromImport('{}.{}'.format(self._vars['oldmod'].__name__, name))
		
		# check if name in exports
		if self._vars['exports'] and name not in self._vars['exports'] and rname not in self._vars['exports']:
			raise NameNotExportable('{}.{}'.format(self._vars['oldmod'].__name__, name))
		
		# check if name exists
		if hasattr(self._vars['oldmod'], rname):
			return getattr(self._vars['oldmod'], rname)
		
		if callable(self._vars['delegate']):
			return self._vars['delegate'](name)

		try:
			return self._vars['oldmod']._modkit_delegate(name)
		except (AttributeError):
			raise NameNotExists('{}.{}'.format(self._vars['oldmod'].__name__, rname) 
				+ ('(a.k.a {})'.format(name) if name != rname else ''))

class Modkit(object):

	def __init__(self):
		# whereever imports this module directly
		frame = None
		for f in inspect.getouterframes(inspect.currentframe())[2:]:
			if f[0].f_code.co_filename.startswith('<frozen importlib'):
				continue
			frame = f[0]
			break
		mymod = inspect.getmodule(frame)
		if mymod.__name__ == '__main__':
			raise ImportError('modkit is intended to be used in a module other than a script.')

		self.module = Module(mymod)
		sys.modules[mymod.__name__] = self.module

	def exports(self, *names):
		self.module._vars['exports'] |= set(names)

	def ban(self, *names):
		self.module._vars['banned'] |= set(names)

	def unban(self, *names):
		self.module._vars['banned'] -= set(names)

	def alias(self, frm, to):
		self.module._vars['alias'][to] = frm

	def delegate(self, func):
		if not callable(func):
			raise TypeError('modkit delegate requires a callable.')
		self.module._vars['delegate'] = func
		self.ban(func.__name__)

modkit = Modkit()
