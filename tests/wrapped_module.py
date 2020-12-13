from modkit import *

d = {}

def __getattr__(name):
    return name.upper()

def __getitem__(name):
    return name.lower()

def __call__(baked_name):
    return bake(baked_name)

install()
