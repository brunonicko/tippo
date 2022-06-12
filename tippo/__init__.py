import collections.abc as _collections_abc
import types as _types
import typing as _typing
from typing import *  # noqa
from weakref import (
    ref,  # noqa
    ReferenceType,
    WeakKeyDictionary,
    WeakValueDictionary,
    WeakSet,
)

from typing_extensions import *  # type: ignore


def is_generic(typ: _typing.Type) -> bool:
    return (
        isinstance(typ, type)
        and issubclass(typ, getattr(_typing, "Generic"))
        or isinstance(typ, getattr(_typing, "_GenericAlias"))
        and getattr(typ, "__origin__") not in (_typing.Union, tuple, _typing.ClassVar, _collections_abc.Callable)
    )


class _GenericInfo(_typing.NamedTuple):
    names: _typing.Tuple[str, ...]
    vars: _typing.Tuple[_typing.TypeVar, ...]


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

    _generic = _types.new_class(_base.__name__, (_base, _typing.Generic[_vars]))

    for _name in _names:
        globals()[_name] = _generic
