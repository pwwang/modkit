from __future__ import print_function
import moduleExports as me

print('1, expected')
print(me.a)

print('NameNotImportable, expected')
try:
	print(me.b)
except Exception as ex:
	print(type(ex).__name__)

print('3, expected')
print(me.c())

print('delegated.x, expected')
print(me.x)

print('NameNotImportable, expected')
try:
	print(me.y)
except Exception as ex:
	print(type(ex).__name__)

print('NameNotImportable, expected')
try:
	from moduleExports import b
except Exception as ex:
	print(type(ex).__name__)

print('delegated.x, expected')
from moduleExports import x
print(x)

print('NameNotImportable, expected')
try:
	from moduleExports import y
except Exception as ex:
	print(type(ex).__name__)