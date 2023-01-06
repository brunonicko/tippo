.. logo_start
.. raw:: html

   <p align="center">
     <a href="https://github.com/brunonicko/tippo">
         <picture>
            <object data="./_static/tippo.svg" type="image/png">
                <source srcset="./docs/source/_static/tippo_white.svg" media="(prefers-color-scheme: dark)">
                <img src="./docs/source/_static/tippo.svg" width="60%" alt="tippo" />
            </object>
         </picture>
     </a>
   </p>
.. logo_end

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
Use the latest type annotation features in older versions of Python.

Motivation
----------
When working with Python development for VFX pipelines we are often stuck with older Python versions for the runtime.

`Tippo` aims to bridge that gap since it allows us to use features such as static type checking (which could be
performed by newer Python versions with support for MyPy during the testing phase) even though the code might be
designed to run in Python 2.7, for example.

Installation
------------
`Tippo` is available through `pip`:

``pip install tippo``

Usage
-----
Instead of importing from `typing` and/or `typing_extensions`...

.. code:: python

    >>> try:
    ...     from typing import TypeAlias
    ... except ImportError:
    ...     from typing_extensions import TypeAlias
    ...
    >>> try:
    ...     from typing import final
    ... except ImportError:
    ...     from typing_extensions import final
    ...

...just import directly from `tippo`:

.. code:: python

    >>> from tippo import Generic, final

Generic Fixes
-------------
`Tippo` patches `GenericMeta` to fix known bugs for the Python 2.7 version of `typing` that were not addressed since
it's not officially supported anymore.

Generic class comparison:

.. code:: python

    >>> from tippo import Mapping
    >>> assert Mapping[str, int] == Mapping[str, int]  # passes
    >>> assert not (Mapping[str, int] != Mapping[str, int])  # passes

Subclassing a generic class with a `__weakref__` slot:

.. code:: python

    >>> from weakref import ref
    >>> from tippo import Generic, TypeVar
    >>> T = TypeVar("T")
    >>> class MyGeneric(Generic[T]):
    ...     __slots__ = ("__weakref__",)
    ...
    >>> class SubClass(MyGeneric[T]):  # does not error out
    ...     __slots__ = ()
    ...
    >>> instance = SubClass()
    >>> instance_ref = ref(instance)

In order to maintain the same interface, `GenericMeta` points to `type` when imported from `tippo` in newer versions of
Python.

Backports
---------
Features from the latest versions of Python, such as `TypeAlias`, `ClassVar`, `NewType`, `get_origin`, and `get_args`.

.. code:: python

    >>> from tippo import Mapping, get_args, get_name
    >>> mapping_type = Mapping[str, int]
    >>> [get_name(a) for a in get_args(mapping_type)]
    ['str', 'int']

Generic Weak Structures
-----------------------
Generic versions of weak data structures that work with older Python versions' type annotations.

.. code:: python

    >>> from tippo import Any, ReferenceType, WeakSet, WeakKeyDictionary, WeakValueDictionary, TypeAlias
    >>> class Foo(object):
    ...     pass
    >>> FooWeakRef = ReferenceType[Foo]  # type: TypeAlias
    >>> FooWeakSet = WeakSet[Foo]  # type: TypeAlias
    >>> FooWeakKeyDictionary = WeakKeyDictionary[Foo, Any]  # type: TypeAlias
    >>> FooWeakValueDictionary = WeakValueDictionary[Any, Foo]  # type: TypeAlias

Commonly Used Protocols
-----------------------
Such as:

- `tippo.SupportsGetItem`
- `tippo.SupportsGetSetItem`
- `tippo.SupportsGetSetDeleteItem`
- `tippo.SupportsKeysAndGetItem`

.. code:: python

    >>> from tippo import SupportsGetItem
    >>> class Foo(object):
    ...     def __getitem__(self, item):
    ...         # type: (str) -> int
    ...         return 3
    ...
    >>> def get_stuff(bar):
    ...     # type: (SupportsGetItem[str, int]) -> int
    ...     return bar["stuff"]
    ...
    >>> assert get_stuff(Foo()) == 3  # passes static type checking
    >>> assert get_stuff({"stuff": 3}) == 3  # passes static type checking
