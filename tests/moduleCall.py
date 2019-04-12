from modkit import modkit

A = 1

def _modkit_delegate(name):
	if name == 'x':
		return 'x'

def _modkit_call(module, x):
	setattr(module, 'A', x)
	return module