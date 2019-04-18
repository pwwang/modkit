from __future__ import print_function
import moduleCall

print('1, expected')
print(moduleCall.A)

moduleCall2 = moduleCall(2)
print('1, expected ## make sure it is not changed.')
print(moduleCall.A)
print('2, expected')
print(moduleCall2.A)
from moduleCall2 import A

print('2, expected')
print(A)
print('1, expected')
print(moduleCall.A)

from moduleCall2 import x
print('x, expected')
print(x)

print('x, expected')
print(moduleCall.x)

from moduleCall import A
print('1, expected')
print(A)