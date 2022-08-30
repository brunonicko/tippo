from __future__ import absolute_import, division, print_function

import functools as _functools
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
import typing_extensions as _typing_extensions
from typing_extensions import *  # type: ignore


# Prepare __all__ by combining typing + typing_extensions.
_all_ = _typing.__all__ + _typing_extensions.__all__  # type: ignore
globals()["__all__"] = _all_


def _update_all(*_members):
    _all_.extend(set(_members).difference(_all_))


# Forward reference type.
try:
    from typing import ForwardRef
except ImportError:
    from typing import _ForwardRef as ForwardRef  # type: ignore  # noqa

    _update_all("ForwardRef")


# Mappings.
_BUILTINS_MAPPING = {
    List: list,
    Set: set,
    Dict: dict,
    Tuple: tuple,
    Type: type,
}
_BUILTINS_MAPPING.update(
    dict(
        (getattr(_typing, n, getattr(_typing_extensions, n, None)), getattr(_collections_abc, n))
        for n in set(_collections_abc.__all__).intersection(
            _typing.__all__ + _typing_extensions.__all__  # type: ignore
        )
        if not n.startswith("_")
    )
)
assert None not in _BUILTINS_MAPPING
_TYPING_MAPPING = dict((b, t) for t, b in _BUILTINS_MAPPING.items())


def get_builtin(typ):
    """
    Get equivalent builtin.

    :param typ: Type.
    :return: Builtin type.
    """
    return _BUILTINS_MAPPING.get(typ, typ)


def get_typing(typ):
    """
    Get equivalent typing.

    :param typ: Type.
    :return: Typing type.
    """
    return _TYPING_MAPPING.get(typ, typ)


_update_all("get_builtin", "get_typing")


# Fix GenericMeta not equals comparison for Python 2.7.
try:
    from typing import GenericMeta as _GenericMeta  # type: ignore
except ImportError:
    pass
else:

    def __ne__(cls, other):
        is_equal = cls == other
        if is_equal is NotImplemented:
            return NotImplemented
        else:
            return not is_equal

    __ne__.__module__ = _GenericMeta.__module__
    type.__setattr__(_GenericMeta, "__ne__", __ne__)
    _update_all("GenericMeta")


# Add missing final decorator for older Python versions.
if "final" not in globals():

    def final(f):  # type: ignore
        """A decorator to indicate final methods and final classes."""
        return f

    _update_all("final")


# Add missing inspection functions for older Python versions.
if "get_origin" not in globals():
    from typing_inspect import get_origin as _get_origin  # type: ignore

    @_functools.wraps(_get_origin)
    def get_origin(typ):
        if typ is Generic:
            return Generic

        if typ in (Union, Literal, Final, ClassVar):
            return None

        for name, origin in {"_Literal": Literal, "_ClassVar": ClassVar, "_Final": Final}.items():
            if type(typ) is getattr(_typing, name, None):
                return origin

        return _get_origin(typ)

    _update_all("get_origin")


if "get_args" not in globals():
    from typing_inspect import get_args as _get_args  # type: ignore

    @_functools.wraps(_get_args)
    def get_args(typ):
        return _get_args(typ, True)

    _update_all("get_args")


# Build missing generic types.
_GenericInfo = _typing.NamedTuple(
    "_GenericInfo",
    (
        ("names", "_typing.Tuple[str, ...]"),
        ("args", "_typing.Tuple[_typing.TypeVar, ...]"),
    ),
)

_T = _typing.TypeVar("_T")
_KT = _typing.TypeVar("_KT")
_VT_co = _typing.TypeVar("_VT_co", covariant=True)
_T_co = _typing.TypeVar("_T_co", covariant=True)

_GENERIC_TYPES = {
    ReferenceType: _GenericInfo(
        names=("ReferenceType", "ref"),
        args=(_typing.cast(_typing.TypeVar, _T),),
    ),
    WeakSet: _GenericInfo(
        names=("WeakSet",),
        args=(_typing.cast(_typing.TypeVar, _T_co),),
    ),
    WeakKeyDictionary: _GenericInfo(
        names=("WeakKeyDictionary",),
        args=(_typing.cast(_typing.TypeVar, _KT), _typing.cast(_typing.TypeVar, _VT_co)),
    ),
    WeakValueDictionary: _GenericInfo(
        names=("WeakValueDictionary",),
        args=(_typing.cast(_typing.TypeVar, _KT), _typing.cast(_typing.TypeVar, _VT_co)),
    ),
}

for _base, (_names, _vars) in _GENERIC_TYPES.items():
    _update_all(*_names)

    if hasattr(_base, "__class_getitem__") or hasattr(type(_base), "__getitem__"):
        continue

    if hasattr(_types, "new_class"):
        _generic = _types.new_class(_base.__name__, (_base, _typing.Generic[_vars]))  # type: ignore
    elif hasattr(_typing, "GenericMeta"):
        _generic = _typing.GenericMeta(_base.__name__, (_base, _typing.Generic[_vars]), {})  # type: ignore
    else:
        _generic = type(_base.__name__, (_base, _typing.Generic[_vars]), {})  # type: ignore

    for _name in _names:
        globals()[_name] = _generic


# Function to get type name that supports generics.
_SPECIAL_NAMES = {
    Any: "Any",
    ClassVar: "ClassVar",
    Optional: "Optional",
    Literal: "Literal",
    Final: "Final",
    Union: "Union",
    ForwardRef: "ForwardRef",
    Ellipsis: "...",
    None: "None",
    type(None): "NoneType",
    True: "True",
    False: "False",
    NotImplemented: "NotImplemented",
    type(NotImplemented): "NotImplementedType",
}


def get_name(typ, qualname_getter=lambda t: getattr(t, "__qualname__", None)):
    # type: (Any, Callable[[Any], Optional[str]]) -> Optional[str]
    """
    Get name.

    :param typ: Type/typing form.
    :param qualname_getter: Qualified name getter function override.
    :return: Name or None.
    """
    name = None

    # Special name.
    try:
        if typ in _SPECIAL_NAMES:
            name = _SPECIAL_NAMES[typ]
    except TypeError:  # ignore non-hashable
        pass

    # Python 2.7.
    if name is None:
        if not hasattr(typ, "__forward_arg__") and type(typ).__module__ in ("typing", "typing_extensions", "tippo"):
            if type(typ).__name__.lstrip("_") == "Literal":
                return "Literal"
            if type(typ).__name__.lstrip("_") == "Final":
                return "Final"
            if type(typ).__name__.lstrip("_") == "ClassVar":
                return "ClassVar"

    # Try a couple of other ways to get the name.
    if name is None:

        # Get origin name.
        origin = get_origin(typ)
        if origin is not None:
            origin_name = (
                qualname_getter(origin)
                or getattr(origin, "__name__", None)
                or getattr(origin, "_name", None)
                or getattr(origin, "__forward_arg__", None)
            )
        else:
            origin_name = None

        # Get the name.
        name = (
            qualname_getter(typ)
            or getattr(typ, "__name__", None)
            or getattr(typ, "_name", None)
            or getattr(typ, "__forward_arg__", None)
        )

        # We have an origin name.
        if origin_name:

            # But we don't have a name. Use the origin name instead.
            if not name:
                name = origin_name

            # Prefer the origin name if longer and (for qualified generic names).
            elif name and origin_name.endswith(name) and len(origin_name) > len(name):
                name = origin_name

        # Special cases.
        elif not name:
            for cls_name, special_name in {
                "_Literal": "Literal",
                "_ClassVar": "ClassVar",
                "_Final": "Final",
                "_Union": "Union",
            }.items():
                cls = getattr(_typing, cls_name, None)
                if type(typ) is cls or origin is not None and type(origin) is cls:
                    name = special_name
                    break

    return name or None


_update_all("get_name")
