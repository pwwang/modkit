from __future__ import print_function
import moduleWildExports as mwe

print('1, expected')
print(mwe.aa)

print('NameNotImportable, expected')
try:
	print(mwe.b)
except Exception as ex:
	print(type(ex).__name__)

print('3, expected')
print(mwe.ac())

from moduleWildExports import *

print('1, expected')
print(aa)

print('NameError, expected')
try:
	print(b)
except Exception as ex:
	print(type(ex).__name__)

print('3, expected')
print(ac())
