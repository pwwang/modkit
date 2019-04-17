from modkit import Modkit
modkit = Modkit()
modkit.ban('a', 'c', 'x')

a = 1
b = 2
def c():
	return 3

def delegate(name):
	if name == 'call':
		def func(prefix):
			return prefix + '.' + name
		return func
	return 'delegated.' + name

modkit.delegate(delegate)