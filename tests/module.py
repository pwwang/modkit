"""A module for test with full functionalities of modkit"""
from modkit import modkit

MUTABLE = {}
IMMUTABLE = 1

BANNED_NAME1 = 1
BANNED_NAME2 = 2
THIS_IS_ALSO_BANNED = 3

EXPORT_ABLE = 1
EXPORT_ABLE2 = 1
THIS_IS_ALSO_EXPORTABLE = 3

@modkit.delegate
def delegate(name):
    return name

@modkit.call
def call(module, assigned_to):
    return module.__bake__(assigned_to)

def func(a):
    MUTABLE['a'] = a

modkit.export('*')
modkit.ban('BANNED_*', 'THIS_IS_ALSO_BANNED')
