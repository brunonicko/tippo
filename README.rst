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
`Tippo` provides a cleaner and forward compatible way to use features from the `typing` and `typing_extension` modules
on python 3.7+.

Example
-------

Instead of using a try block for forward compatibility:

.. code:: python

    >>> try:
    ...     from typing import Annotated
    ... except ImportError:
    ...     from typing_extensions import Annotated
    ...
    >>> try:
    ...     from typing import final
    ... except ImportError:
    ...     from typing_extensions import final
    ...

Just import from `tippo` instead:

.. code:: python

    >>> from tippo import Annotated, final

Generic Weak Structures
-----------------------

`Tippo` also implements generic versions of weak data structures that work with older python versions' type annotations:

.. code:: python

    >>> from tippo import Any, ReferenceType, WeakSet, WeakKeyDictionary, WeakValueDictionary
    >>> class X:
    ...     pass
    >>> weak_ref: ReferenceType[X]
    >>> weak_set: WeakSet[X]
    >>> weak_key_dict: WeakKeyDictionary[X, Any]
    >>> weak_value_dict: WeakKeyDictionary[Any, X]
