modkit = __import__('modkit').modkit

MUTABLE = {'a': 1}

@modkit.call
def call(module, assigned_to):
    if not assigned_to:
        raise ValueError('No name assigned.')
    newmod = module.__bake__(assigned_to, deep=False)
    return newmod
