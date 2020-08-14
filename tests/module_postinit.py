from modkit import modkit

@modkit.postinit
def postinit(module):
    module.a = 1
