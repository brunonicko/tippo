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


class _GenericInfo(_typing.NamedTuple):
    names: _typing.Tuple[str, ...]
    vars: _typing.Tuple[_typing.TypeVar, ...]


_T = _typing.TypeVar("_T")
_GENERIC_TYPES = {
    ReferenceType: _GenericInfo(
        names=("ReferenceType", "ref"),
        vars=(_typing.cast(_typing.TypeVar, _T),),
    ),
    WeakSet: _GenericInfo(
        names=("WeakSet",),
        vars=getattr(_typing.AbstractSet, "__parameters__"),
    ),
    WeakKeyDictionary: _GenericInfo(
        names=("WeakKeyDictionary",),
        vars=getattr(_typing.Mapping, "__parameters__"),
    ),
    WeakValueDictionary: _GenericInfo(
        names=("WeakValueDictionary",),
        vars=getattr(_typing.Mapping, "__parameters__"),
    ),
}


for _base, (_names, _vars) in _GENERIC_TYPES.items():
    if hasattr(_base, "__class_getitem__"):
        continue

    _generic = _types.new_class(_base.__name__, (_base, _typing.Generic[_vars]))

    for _name in _names:
        globals()[_name] = _generic
