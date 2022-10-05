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
`Tippo` provides a cleaner and compatible way to use features from both `typing` and `typing_extension` across a wide
range of Python versions, including Python 2.7.

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

Also, in order to maintain the same interface, `GenericMeta` points to `type` when imported from `tippo` in newer
versions of Python.

Missing Features
----------------
`Tippo` back-ports some features from future versions of Python to older ones, such as `TypeAlias`, `ClassVar`,
`NewType`, `get_origin`, and `get_args`.

.. code:: python

    >>> from tippo import Mapping, get_args, get_name
    >>> mapping_type = Mapping[str, int]
    >>> [get_name(a) for a in get_args(mapping_type)]
    ['str', 'int']

Generic Weak Structures
-----------------------

`Tippo` also implements generic versions of weak data structures that work with older Python versions' type annotations
without the need to defer their evaluation:

.. code:: python

    >>> from tippo import Any, ReferenceType, WeakSet, WeakKeyDictionary, WeakValueDictionary
    >>> class Foo(object):
    ...     pass
    >>> weak_ref = ReferenceType[Foo](Foo())
    >>> weak_set = WeakSet[Foo]({Foo()})
    >>> weak_key_dict = WeakKeyDictionary[Foo, Any]({Foo(): "foo"})
    >>> weak_value_dict = WeakValueDictionary[Any, Foo]({"foo": Foo()})
