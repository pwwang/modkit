"""from xxx import *
is only allowed at module level.
However, to do it with pytest, an
import file mismatch
will happen.

Here we do it here and call it in pytest
"""
from module_everything import *

def get_a():
    return everything_a

def get_b():
    return everything_b

def get_c():
    try:
        return everything_c
    except NameError:
        return 'NameError'

# should be exactly:
# 12NameError
print(f"{get_a()}{get_b()}{get_c()}", end='')
