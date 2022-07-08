Tippo
=====
.. image:: https://github.com/brunonicko/tippo/workflows/MyPy/badge.svg
   :target: https://github.com/brunonicko/tippo/actions?query=workflow%3AMyPy

.. image:: https://github.com/brunonicko/tippo/workflows/Lint/badge.svg
   :target: https://github.com/brunonicko/tippo/actions?query=workflow%3ALint

.. image:: https://github.com/brunonicko/tippo/workflows/Tests/badge.svg
   :target: https://github.com/brunonicko/tippo/actions?query=workflow%3ATests

.. image:: https://readthedocs.org/projects/tippo/badge/?version=stable
   :target: https://tippo.readthedocs.io/en/stable/

.. image:: https://img.shields.io/github/license/brunonicko/tippo?color=light-green
   :target: https://github.com/brunonicko/tippo/blob/main/LICENSE

.. image:: https://static.pepy.tech/personalized-badge/tippo?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads
   :target: https://pepy.tech/project/tippo

.. image:: https://img.shields.io/pypi/pyversions/tippo?color=light-green&style=flat
   :target: https://pypi.org/project/tippo/

Overview
--------
`Tippo` provides a cleaner and compatible way to use features from both `typing` and `typing_extension` with a wide
range of python versions.

Example
-------

Instead of using an ugly try block for forwards compatibility...

.. code:: python

    >>> try:
    ...     from typing import Generic
    ... except ImportError:
    ...     from typing_extensions import Generic
    ...
    >>> try:
    ...     from typing import final
    ... except ImportError:
    ...     from typing_extensions import final
    ...

...just import directly from `tippo`!

.. code:: python

    >>> from tippo import Generic, final

Generic Weak Structures
-----------------------

`Tippo` also implements generic versions of weak data structures that work with older python versions' type annotations
without the need to defer their evaluation:

.. code:: python

    >>> from tippo import Any, ReferenceType, WeakSet, WeakKeyDictionary, WeakValueDictionary
    >>> class Foo(object):
    ...     pass
    >>> weak_ref = ReferenceType(Foo())  # type: ReferenceType[Foo]
    >>> weak_set = WeakSet({Foo()})  # type: WeakSet[Foo]
    >>> weak_key_dict = WeakKeyDictionary({Foo(): "foo"})  # type: WeakKeyDictionary[Foo, Any]
    >>> weak_value_dict = WeakValueDictionary({"foo": Foo()})  # type: WeakValueDictionary[Any, Foo]
