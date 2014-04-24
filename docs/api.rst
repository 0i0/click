API
===

.. module:: click

This part of the documentation shows the full API reference of all public
classes and functions.

Decorators
----------

.. autofunction:: command

.. autofunction:: group

.. autofunction:: argument

.. autofunction:: option

.. autofunction:: password_option

.. autofunction:: confirmation_option

.. autofunction:: version_option

.. autofunction:: help_option

Helper Functions
----------------

.. autofunction:: prompt

.. autofunction:: confirm

.. autofunction:: get_terminal_size

Commands
--------

.. autoclass:: Command
   :members:

.. autoclass:: MultiCommand
   :members:

.. autoclass:: Group
   :members:

Parameters
----------

.. autoclass:: Parameter
   :members:

.. autoclass:: Option

.. autoclass:: Argument

Context
-------

.. autoclass:: Context
   :members:

Types
-----

.. autodata:: STRING

.. autodata:: INT

.. autodata:: FLOAT

.. autodata:: BOOL

.. autoclass:: File

.. autoclass:: ParamType

Exceptions
----------

.. autoexception:: Abort

.. autoexception:: UsageError
