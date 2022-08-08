from __future__ import absolute_import, division, print_function

import inspect as _inspect
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

from six import moves as _moves

# Import typing.
import typing as _typing
from typing import *  # noqa

# Import typing extensions.
import typing_extensions as _typing_extensions
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


# Add missing features for older Python versions.
if "final" not in globals():

    def final(f):  # type: ignore
        """A decorator to indicate final methods and final classes."""
        return f


if "get_origin" not in globals():

    def get_origin(typ):  # type: ignore
        """
        Get the unsubscripted version of a type.

        :param typ: Type.
        :return: Unsubscripted version of a type.
        """
        if hasattr(typ, "__origin__"):
            origin = typ.__origin__
            if origin is None:
                return typ
            return origin
        if typ is Generic:
            return typ
        if type(typ).__module__ == "typing":
            if type(typ).__name__.strip("_") == "Literal":
                return Literal
            if type(typ).__name__.strip("_") == "Final":
                return Final
            if type(typ).__name__.strip("_") == "ClassVar":
                return ClassVar
        return None


if "get_args" not in globals():

    def _is_param_expr(arg):
        extra_param_types = (tuple, list)
        if "ParamSpec" in globals():
            extra_param_types += (ParamSpec,)
        _ConcatenateGenericAlias = getattr(
            _typing, "_ConcatenateGenericAlias", getattr(_typing_extensions, "_ConcatenateGenericAlias", None)
        )
        if _ConcatenateGenericAlias is not None:
            extra_param_types += (_ConcatenateGenericAlias,)
        return arg is Ellipsis or isinstance(arg, extra_param_types)

    def get_args(typ):  # type: ignore
        """
        Get type arguments.

        :param typ: Type.
        :return: Type arguments.
        """

        # No "__args__".
        if not hasattr(typ, "__args__"):
            if hasattr(typ, "__type__") and type(typ).__name__.strip("_") == "ClassVar":
                return (typ.__type__,)
            if type(typ).__module__ == "typing":
                if type(typ).__name__.strip("_") == "Literal" and hasattr(typ, "__values__"):
                    return typ.__values__
                if type(typ).__name__.strip("_") in ("Final", "ClassVar") and hasattr(typ, "__type__"):
                    return (typ.__type__,)
            return None

        # Has args.
        args = typ.__args__
        if args is None:
            return None

        # Standardize callable type.
        callable_type = _moves.collections_abc.Callable  # type: ignore
        if get_origin(typ) in (callable_type, Callable) and not (len(args) == 2 and _is_param_expr(args[0])):
            args = (list(args[:-1]), args[-1])

        return args


# Utility functions.
_SPECIAL_NAMES = {
    Ellipsis: "...",
    None: "None",
    type(None): "NoneType",
    True: "True",
    False: "False",
    NotImplemented: "NotImplemented",
    type(NotImplemented): "NotImplementedType",
    Literal: "Literal",
    Final: "Final",
    ClassVar: "ClassVar",
}


def get_name(typ, force_typing_name=False, name_getter=None):
    # type: (Any, bool, Callable[[Any], str] | None) -> str | None
    """
    Get name.

    :param typ: Type/typing form.
    :param force_typing_name: Whether to force the typing form name over builtin (example: `Dict` instead of `dict`).
    :param name_getter: Custom callable that can be used to try to get the name first.
    :return: Name or None.
    :raises TypeError: Could not get name for typing argument.
    """
    name = None

    # Use custom name getter callable if provided.
    if name_getter is not None:
        name = name_getter(typ)

    # Special name.
    if name is None:
        try:
            if typ in _SPECIAL_NAMES:
                name = _SPECIAL_NAMES[typ]
        except TypeError:  # ignore non-hashable
            pass

    # Python 2.7.
    if type(typ).__module__ == "typing":
        if type(typ).__name__.strip("_") == "Literal":
            return "Literal"
        if type(typ).__name__.strip("_") == "Final":
            return "Final"
        if type(typ).__name__.strip("_") == "ClassVar":
            return "ClassVar"

    # Try a couple of ways to get the name.
    if name is None:

        # Get origin name.
        origin = get_origin(typ)
        if origin is not None:
            origin_type = origin
        else:
            origin_type = typ
        origin_name = (
            getattr(origin_type, "__qualname__", None)
            or getattr(origin_type, "__name__", None)
            or getattr(origin_type, "_name", None)
            or getattr(origin_type, "__forward_arg__", None)
        )

        # Get the name.
        name = (
            getattr(typ, "__qualname__", None)
            or getattr(typ, "__name__", None)
            or getattr(typ, "_name", None)
            or getattr(typ, "__forward_arg__", None)
        )

        # Choose the origin name if longer (for qualified generic names).
        if origin_name is not None and name is not None and len(origin_name) > len(name):
            name = origin_name

        # Try to get the name from the origin.
        if name is None and origin is not None:
            name = getattr(origin, "_name", None)
            if name is None and not _inspect.isclass(typ):
                name = getattr(typ.__class__, "__qualname__", typ.__class__.__name__).strip("_")

    # Could not get it.
    if name is None:
        return None

    # Force typing name if possible.
    module = getattr(typ, "__module__", None)
    if force_typing_name and module == _moves.builtins.__name__:
        typing_name = name.strip("_").capitalize()
        if hasattr(_typing, typing_name) or hasattr(_typing_extensions, typing_name):
            name = typing_name

    return name


def get_module(typ, force_tippo_module=True):
    # type: (Any, bool) -> str | None
    """
    Get module.

    :param typ: Type/typing form.
    :param force_tippo_module: Whether to force the module to be `tippo` if possible.
    :return: Module or None.
    """
    module = getattr(typ, "__module__", None)
    if module is None:
        return None

    if force_tippo_module:
        if module in ("typing", "typing_extensions") and get_name(typ) in globals():
            module = __name__

    return module


def get_args_paths(args, include_module=True, force_typing_name=False, name_getter=None):
    # type: (Iterable[Any], bool | Literal["auto"], bool, Callable[[Any], str] | None) -> str
    """
    Get arguments' paths.

    :param args: Arguments.
    :param include_module: Whether to always include the module (True), never (False), or only when needed ("auto").
    :param force_typing_name: Whether to force the typing form name over builtin (example: `Dict` instead of `dict`).
    :param name_getter: Custom callable that can be used to get the name for custom behavior.
    :return: Formatted paths for arguments.
    :raises TypeError: Could not get name for typing argument.
    """
    arg_paths = []
    for arg in args:
        if isinstance(arg, Iterable):
            formatted_arg = get_args_paths(
                arg,
                include_module=include_module,
                force_typing_name=force_typing_name,
                name_getter=name_getter,
            )
            arg_paths.append("[{}]".format(formatted_arg))
        else:
            arg_path = get_path(
                arg,
                include_args=True,
                include_module=include_module,
                force_typing_name=force_typing_name,
                name_getter=name_getter,
            )
            if arg_path is None:
                error = "could not get name for typing argument {!r}".format(arg)
                raise TypeError(error)
            arg_paths.append(arg_path)
    formatted_args = ", ".join(arg_paths)
    return formatted_args


def get_path(typ, include_args=True, include_module=True, force_typing_name=False, name_getter=None):
    # type: (Any, bool, bool | Literal["auto"], bool, Callable[[Any], str] | None) -> str | None
    """
    Get typing path or None if not possible.

    :param typ: Type/typing form.
    :param include_module: Whether to always include the module (True), never (False), or only when needed ("auto").
    :param include_args: Whether to include the typing arguments in the name.
    :param force_typing_name: Whether to force the typing form name over builtin (example: `Dict` instead of `dict`).
    :param name_getter: Custom callable that can be used to get the name for custom behavior.
    :return: Name or None.
    """

    # Get the name.
    name = get_name(typ, force_typing_name=force_typing_name, name_getter=name_getter)
    if name is None:
        return None

    # Include typing arguments.
    name_without_args = name
    if include_args:
        args = get_args(typ)
        if args:
            if name == "Literal":
                formatted_args = ", ".join(str(arg) for arg in args)
            else:
                formatted_args = get_args_paths(
                    args,
                    include_module=include_module,
                    force_typing_name=force_typing_name,
                    name_getter=name_getter,
                )
            name = "{}[{}]".format(name, formatted_args)

    # Include module.
    module = getattr(typ, "__module__", None)
    if module is not None:
        if (include_module is True and module != _moves.builtins.__name__) or (
            include_module == "auto"
            and module not in (None, "typing", "typing_extensions", __name__, _moves.builtins.__name__)
        ):
            if module in ("typing", "typing_extensions") and name_without_args in globals():
                module = __name__
            name = "{}.{}".format(module, name)

    return name
