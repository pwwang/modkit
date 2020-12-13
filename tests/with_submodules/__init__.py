from modkit import *

def __getattr__(name):
    submod = submodule(name, __name__)
    if submod:
        return submod

    return name.upper()

def __call__(baked_name):
    return bake(baked_name)

install()
