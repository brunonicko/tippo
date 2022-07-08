from __future__ import absolute_import, division, print_function

import types as _types
from weakref import (
    ref,  # noqa
    ReferenceType,
    WeakKeyDictionary,
    WeakValueDictionary,
    WeakSet,
)

try:
    import collections.abc as _collections_abc
except ImportError:
    import collections as _collections_abc  # type: ignore

# Import typing.
import typing as _typing
from typing import *  # noqa

# Import typing extensions.
from typing_extensions import *  # type: ignore

# Fix GenericMeta not equals comparison for Python 2.7.
try:
    from typing import GenericMeta as _GenericMeta  # type: ignore
except ImportError:
    pass
else:

    def __ne__(cls, other):
        is_equal = cls.__eq__(other)
        if is_equal is NotImplemented:
            return NotImplemented
        else:
            return not is_equal

    __ne__.__module__ = _GenericMeta.__module__
    type.__setattr__(_GenericMeta, "__ne__", __ne__)


def is_generic(typ):
    # type: (_typing.Type) -> bool
    """
    Tell whether a class is generic or not.

    :param typ: Class.
    :return: True if generic.
    """
    return (
        isinstance(typ, type)
        and issubclass(typ, getattr(_typing, "Generic"))
        or isinstance(typ, getattr(_typing, "_GenericAlias"))
        and getattr(typ, "__origin__")
        not in (_typing.Union, tuple, _typing.ClassVar, _typing.Callable, _collections_abc.Callable)
    )


# Build missing generic types.
_GenericInfo = _typing.NamedTuple(
    "_GenericInfo",
    (
        ("names", "_typing.Tuple[str, ...]"),
        ("vars", "_typing.Tuple[_typing.TypeVar, ...]"),
    ),
)

_T = _typing.TypeVar("_T")
_KT = _typing.TypeVar("_KT")
_VT_co = _typing.TypeVar("_VT_co", covariant=True)
_T_co = _typing.TypeVar("_T_co", covariant=True)

_GENERIC_TYPES = {
    ReferenceType: _GenericInfo(
        names=("ReferenceType", "ref"),
        vars=(_typing.cast(_typing.TypeVar, _T),),
    ),
    WeakSet: _GenericInfo(
        names=("WeakSet",),
        vars=(_typing.cast(_typing.TypeVar, _T_co),),
    ),
    WeakKeyDictionary: _GenericInfo(
        names=("WeakKeyDictionary",),
        vars=(_typing.cast(_typing.TypeVar, _KT), _typing.cast(_typing.TypeVar, _VT_co)),
    ),
    WeakValueDictionary: _GenericInfo(
        names=("WeakValueDictionary",),
        vars=(_typing.cast(_typing.TypeVar, _KT), _typing.cast(_typing.TypeVar, _VT_co)),
    ),
}

for _base, (_names, _vars) in _GENERIC_TYPES.items():
    if is_generic(_base):
        continue

    _generic = _types.new_class(_base.__name__, (_base, _typing.Generic[_vars]))  # type: ignore

    for _name in _names:
        globals()[_name] = _generic


# Add missing final for older Python versions.
if "final" not in globals():

    def final(f):  # type: ignore
        return f
