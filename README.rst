
modkit
======


.. image:: https://img.shields.io/pypi/v/modkit?style=flat-square
   :target: https://pypi.org/project/modkit/
   :alt: Pypi


.. image:: https://img.shields.io/github/tag/pwwang/modkit?style=flat-square
   :target: https://github.com/pwwang/modkit
   :alt: Github


.. image:: https://img.shields.io/pypi/pyversions/modkit?style=flat-square
   :target: https://pypi.org/project/modkit/
   :alt: PythonVers


Tweak your modules the way you want

Installation
------------

.. code-block:: shell

   pip install -U modkit

Usage
-----

``module.py``

.. code-block:: python

   import modkit

   a = 1
   d = {}

   def __getattr__(name):
       # we have this supported with python3.7+
       # but with modkit, you can do it with python3.6+
       return name.upper()

   def __getitem__(name):
       return name.lower()

   def __call__(name):
       return name * 2

   modkit.install()

.. code-block:: python

   import module

   module.a # 1
   module.b # B
   module.d # {}
   module['c'] # C
   module('e') # ee

Baking a module
^^^^^^^^^^^^^^^

You can make a copy of your module with modkit easily.

``module.py``

.. code-block:: python

   from modkit import install, bake

   d = {}

   def __call__():
       module2 = bake()
       return module2
       # or return bake('module2')

   install()

.. code-block:: python

   import module

   m2 = module()
   m2
   # <module 'module2' from './module.py' (wrapped by modkit)>
   m2.__name__ # 'module2
   m2.d['a'] = 1

   module.d == {}

Note that baking re-execute the original module and generate a new module.

Submodules
^^^^^^^^^^

Say we have following structure:

.. code-block::

   |- module
      |- __init__.py
      |- sub.py

If ``__getattr__`` is defined in ``__init__.py``\ , when we do:

.. code-block:: python

   from module import sub
   # or
   # import module
   # module.sub

``__getattr__`` will first handle this, meaning the ``sub`` module will not be imported as expected. You have to do it inside ``__getattr__``\ :

``modkit`` has a helper function ``submodule``\ , which tries to import the submodule under current one.

.. code-block:: python

   from modkit import install, submodule
   def __getattr__(name):
       submod = submodule(name)
       if submod:
           # submodule imported
           return submod
       # other stuff you want to do with name
       # or raise error

   install()

Then ``from module import sub`` or ``module.sub`` will work as expected.

Note that ``submodule`` will not raise ``ImportError``. If import fails, it will return ``None``.

Note that we can also import submodules from a baked module, just like we do for the original module.
