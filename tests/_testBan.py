from __future__ import print_function
import moduleBan as mb

print('NameBannedFromImport, expected')
try:
	print(mb.a)
except Exception as ex:
	print(type(ex).__name__)

print('2, expected')
print(mb.b)

print('NameBannedFromImport, expected')
try:
	print(mb.c())
except Exception as ex:
	print(type(ex).__name__)

print('NameBannedFromImport, expected')
try:
	print(mb.x)
except Exception as ex:
	print(type(ex).__name__)



print('delegated.y, expected')
print(mb.y)

print('2, expected')
from moduleBan import b
print(b)

print('NameBannedFromImport, expected')
try:
	from moduleBan import c
except Exception as ex:
	print(type(ex).__name__)

print('delegated.y, expected')
from moduleBan import y
print(y)

print('NameBannedFromImport, expected')
try:
	from moduleBan import a
except Exception as ex:
	print(type(ex).__name__)