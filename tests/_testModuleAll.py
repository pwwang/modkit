from __future__ import print_function
from moduleAll import *

print('1, expected')
print(a)
print('2, expected')
print(b)
print('3, expected')
print(c())

print('NameError, expected')
try:
	print(x)
except Exception as ex:
	print(type(ex).__name__)

print('NameError, expected')
try:
	print(_modkit_delegate('test'))
except Exception as ex:
	print(type(ex).__name__)

print('NameBannedFromImport, expected')
try:
	from moduleAll import _modkit_delegate
except Exception as ex:
	print(type(ex).__name__)