from modkit import modkit
from . import module_alias as sub
from .module_alias import NAME1, NAME3

@modkit.call
def call(module, assigned_to):
    return module.__bake__(assigned_to)
