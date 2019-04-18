from __future__ import print_function
from modkit import NameBannedFromImport
import moduleAll as ma
import moduleBan as mb

print('1, expected')
print(ma.a)

print('NameBannedFromImport, expected')
try:
	print(mb.a)
except NameBannedFromImport:
	print('NameBannedFromImport')

print('2, expected')
print(ma.b)

print('2, expected')
print(mb.b)

