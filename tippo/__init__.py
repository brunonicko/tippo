import functools as _functools
import typing as _typing
from weakref import ref  # noqa

import six as _six
import typing_extensions as _typing_extensions
from six.moves import collections_abc as _collections_abc
from typing_extensions import *

if True:
    from typing import *  # type: ignore  # noqa


_T = TypeVar("_T")
_KT_contra = TypeVar("_KT_contra", contravariant=True)
_VT_co = TypeVar("_VT_co", covariant=True)
_KT = TypeVar("_KT")


# Prepare __all__ by combining typing + typing_extensions.
_all_ = sorted(str(m) for m in set(_typing.__all__ + _typing_extensions.__all__))
globals()["__all__"] = _all_


def _update_all(*_members):
    # type: (*str) -> None
    _all_.extend(set(str(m) for m in _members).difference(_all_))


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
}  # type: Dict[Any, Any]
_BUILTINS_MAPPING.update(
    dict(
        (
            getattr(_typing, n, getattr(_typing_extensions, n, None)),
            getattr(_collections_abc, n),
        )
        for n in set(getattr(_collections_abc, "__all__")).intersection(
            _typing.__all__ + _typing_extensions.__all__
        )
        if not n.startswith("_")
    )
)
assert None not in _BUILTINS_MAPPING
_TYPING_MAPPING = dict((b, t) for t, b in _BUILTINS_MAPPING.items())


def get_builtin(typ):
    # type: (_T) -> _T
    """
    Get equivalent builtin.

    :param typ: Type.
    :return: Builtin type.
    """
    return cast(_T, _BUILTINS_MAPPING.get(typ, typ))


def get_typing(typ):
    # type: (_T) -> _T
    """
    Get equivalent typing.

    :param typ: Type.
    :return: Typing type.
    """
    return cast(_T, _TYPING_MAPPING.get(typ, typ))


_update_all("get_builtin", "get_typing")


# Patch GenericMeta for Python 2.7 with some fixes.
try:
    from typing import GenericMeta as _GenericMeta  # type: ignore  # noqa
except ImportError:
    GenericMeta = type
else:

    class _Class(Generic[_T]):
        pass

    # Fix not equal operator logic in python 2.
    need_ne_fix = (_Class[int] != _Class[(int,)]) is not False
    if need_ne_fix:

        def __ne__(cls, other):
            # type: (Type[Any], object) -> bool
            is_equal = cls == other
            if is_equal is NotImplemented:
                return NotImplemented
            else:
                return not is_equal

        __ne__.__module__ = _GenericMeta.__module__
        type.__setattr__(_GenericMeta, "__ne__", __ne__)

    # Fix subclassing slotted generic class with __weakref__.
    class _SlottedClass(Generic[_T]):
        __slots__ = ("__weakref__",)

    try:

        class _SlottedSubClass(_SlottedClass[_T]):
            __slots__ = ()

    except TypeError:
        need_weakref_fix = True
    else:
        need_weakref_fix = False

    if need_weakref_fix:
        _original_getitem = getattr(_GenericMeta, "__getitem__")

        @_functools.wraps(_original_getitem)
        def __getitem__(cls, params):
            # type: (Type[_T], Any) -> Type[_T]
            slots = getattr(cls, "__slots__", None)
            if slots is not None and "__weakref__" in slots:
                type.__setattr__(
                    cls, "__slots__", tuple(s for s in slots if s != "__weakref__")
                )
                try:
                    return _original_getitem(cls, params)  # type: ignore
                finally:
                    type.__setattr__(cls, "__slots__", slots)
            else:
                return _original_getitem(cls, params)  # type: ignore

        type.__setattr__(_GenericMeta, "__getitem__", __getitem__)

_update_all("GenericMeta")


# Add missing final decorator for older Python versions.
if "final" not in globals():

    def _final(f):  # type: ignore
        """A decorator to indicate final methods and final classes."""
        return f

    _final.__name__ = _final.__qualname__ = "_final"
    globals()["final"] = _final

    _update_all("final")


class _MissingMeta(type):
    def __getitem__(cls, _):
        # type: (Any) -> Type[Any]
        return cls


# Add missing TypeAlias for older Python versions.
if "TypeAlias" not in globals():

    class _TypeAlias(_six.with_metaclass(_MissingMeta, object)):
        pass

    _TypeAlias.__name__ = _TypeAlias.__qualname__ = "_TypeAlias"
    globals()["TypeAlias"] = _TypeAlias

    _update_all("TypeAlias")


# Add missing ClassVar for older Python versions.
if "ClassVar" not in globals():

    class _ClassVar(_six.with_metaclass(_MissingMeta, object)):
        pass

    _ClassVar.__name__ = _ClassVar.__qualname__ = "_ClassVar"
    globals()["ClassVar"] = _ClassVar

    _update_all("_ClassVar")


# Add missing NewType for older Python versions.
if "NewType" not in globals():

    def _NewType(_name, _typ):  # type: ignore
        return _typ

    _NewType.__name__ = _NewType.__qualname__ = "NewType"
    globals()["NewType"] = _NewType

    _update_all("NewType")


# Add missing Unpack for older Python versions.
if "Unpack" not in globals():

    class _Unpack(_six.with_metaclass(_MissingMeta, object)):
        pass

    _Unpack.__name__ = _Unpack.__qualname__ = "_Unpack"
    globals()["Unpack"] = _Unpack

    _update_all("_Unpack")


# Add missing IO for older Python versions.
if "IO" not in globals():

    class _IO(_six.with_metaclass(_MissingMeta, object)):
        pass

    _IO.__name__ = _IO.__qualname__ = "_IO"
    globals()["IO"] = _IO

    _update_all("_IO")


# Add missing TextIO type for older Python versions.
if "TextIO" not in globals():

    def _TextIO():  # type: ignore
        error = "can't instantiate tippo.TextIO"
        raise TypeError(error)

    _TextIO.__name__ = _TextIO.__qualname__ = "TextIO"
    globals()["TextIO"] = _TextIO

    _update_all("TextIO")


# Add missing BinaryIO type for older Python versions.
if "BinaryIO" not in globals():

    def _BinaryIO():  # type: ignore
        error = "can't instantiate tippo.BinaryIO"
        raise TypeError(error)

    _BinaryIO.__name__ = _BinaryIO.__qualname__ = "BinaryIO"
    globals()["BinaryIO"] = _BinaryIO

    _update_all("BinaryIO")


# Add missing Self type for older Python versions.
if "Self" not in globals():

    def _Self():  # type: ignore
        error = "can't instantiate tippo.Self"
        raise TypeError(error)

    _Self.__name__ = _Self.__qualname__ = "Self"
    globals()["Self"] = _Self

    _update_all("Self")


# Add missing NoReturn type for older Python versions.
if "NoReturn" not in globals():

    def _NoReturn():  # type: ignore
        error = "can't instantiate tippo.NoReturn"
        raise TypeError(error)

    _NoReturn.__name__ = _NoReturn.__qualname__ = "NoReturn"
    globals()["NoReturn"] = _NoReturn

    _update_all("NoReturn")


# Add missing override decorator for older Python versions.
if "override" not in globals():

    def _override(func):  # type: ignore
        return func

    _override.__name__ = _override.__qualname__ = "override"
    globals()["override"] = _override

    _update_all("override")


# Add missing ParamSpec type var for older Python versions.
if "ParamSpec" not in globals():
    assert "ParamSpecArgs" not in globals()
    assert "ParamSpecKwargs" not in globals()

    class _ParamSpec(object):
        def __init__(self, name, bound=None, covariant=False, contravariant=False):
            # type: (str, Any, bool, bool) -> None
            TypeVar(  # noqa
                name,  # noqa
                bound=bound,  # noqa
                covariant=covariant,  # noqa
                contravariant=contravariant,  # noqa
            )  # noqa
            self.__name__ = name
            self.__covariant__ = bool(covariant)
            self.__contravariant__ = bool(contravariant)
            self.__bound__ = bound

        def __or__(self, right):
            # type: (object) -> Any
            return Union[self, right]

        def __ror__(self, left):
            # type: (object) -> Any
            return Union[left, self]

        def __repr__(self):
            # type: () -> str
            if self.__covariant__:
                prefix = "+"
            elif self.__contravariant__:
                prefix = "-"
            else:
                prefix = "~"
            return prefix + self.__name__

        def __reduce__(self):
            # type: () -> str
            return self.__name__

        @property
        def args(self):
            # type: () -> _ParamSpecArgs
            return _ParamSpecArgs(self)

        @property
        def kwargs(self):
            # type: () -> _ParamSpecKwargs
            return _ParamSpecKwargs(self)

    _ParamSpec.__name__ = _ParamSpec.__qualname__ = "ParamSpec"
    globals()["ParamSpec"] = _ParamSpec
    _update_all("ParamSpec")

    class _ParamSpecArgs(object):
        def __init__(self, origin):
            # type: (_ParamSpec) -> None
            self.__origin__ = origin

        def __repr__(self):
            # type: () -> str
            return "{}.args".format(self.__origin__.__name__)

        def __eq__(self, other):
            # type: (object) -> bool
            if not isinstance(other, _ParamSpecArgs):
                return NotImplemented
            return self.__origin__ == other.__origin__

    _ParamSpecArgs.__name__ = _ParamSpecArgs.__qualname__ = "ParamSpecArgs"
    globals()["ParamSpecArgs"] = _ParamSpecArgs
    _update_all("ParamSpecArgs")

    class _ParamSpecKwargs(object):
        def __init__(self, origin):
            # type: (_ParamSpec) -> None
            self.__origin__ = origin

        def __repr__(self):
            # type: () -> str
            return "{}.args".format(self.__origin__.__name__)

        def __eq__(self, other):
            # type: (object) -> bool
            if not isinstance(other, _ParamSpecKwargs):
                return NotImplemented
            return self.__origin__ == other.__origin__

    _ParamSpecKwargs.__name__ = _ParamSpecKwargs.__qualname__ = "ParamSpecKwargs"
    globals()["ParamSpecKwargs"] = _ParamSpecKwargs
    _update_all("ParamSpecKwargs")


# Add missing get_origin function for older Python versions.
if "get_origin" not in globals():
    from typing_inspect import get_origin as _typing_inspect_get_origin  # type: ignore

    def _get_origin(typ):
        # type: (Any) -> Any
        if typ is Generic:
            return Generic

        if typ in (Union, Literal, Final, ClassVar):
            return None

        for name, origin in {
            "_Literal": Literal,
            "_ClassVar": ClassVar,
            "_Final": Final,
        }.items():
            if type(typ) is getattr(_typing, name, None):
                return origin

        return _typing_inspect_get_origin(typ)

    _get_origin.__name__ = _get_origin.__qualname__ = "get_origin"
    _get_origin.__doc__ = _typing_inspect_get_origin.__doc__
    globals()["get_origin"] = _get_origin

    _update_all("get_origin")


# Add missing get_args function for older Python versions.
if "get_args" not in globals():
    from typing_inspect import get_args as _typing_inspect_get_args

    def _get_args(typ):
        # type: (Any) -> Any
        return _typing_inspect_get_args(typ, True)

    _get_args.__name__ = _get_args.__qualname__ = "get_args"
    _get_args.__doc__ = _typing_inspect_get_args.__doc__
    globals()["get_args"] = _get_args

    _update_all("get_args")


# Add missing dataclass_transform function for older Python versions.
if "dataclass_transform" not in globals():

    def _dataclass_transform(
        eq_default=True,  # type: bool
        order_default=False,  # type: bool
        kw_only_default=False,  # type: bool
        field_specifiers=(),  # type: Tuple[Union[Type[Any], Callable[..., Any]], ...]
        **kwargs  # type: Any
    ):
        # type: (...) -> Callable[[_T], _T]
        """
        Decorator that marks a function, class, or metaclass as providing dataclass-like
        behavior.

        The arguments to this decorator can be used to customize this behavior:
        - `eq_default` indicates whether the `eq` parameter is assumed to be True or
          False if it is omitted by the caller.
        - `order_default` indicates whether the `order` parameter is assumed to be True
          or False if it is omitted by the caller.
        - `kw_only_default` indicates whether the `kw_only` parameter is assumed to be
          True or False if it is omitted by the caller.
        - `field_specifiers` specifies a static list of supported classes or functions
          that describe fields, similar to `dataclasses.field()`.

        At runtime, this decorator records its arguments in the
        `__dataclass_transform__` attribute on the decorated object.

        See PEP 681 for more details.
        """

        def decorator(cls_or_fn):
            # type: (_T) -> _T
            cls_or_fn.__dataclass_transform__ = {  # type: ignore
                "eq_default": eq_default,
                "order_default": order_default,
                "kw_only_default": kw_only_default,
                "field_specifiers": field_specifiers,
                "kwargs": kwargs,
            }
            return cls_or_fn

        return decorator

    _dataclass_transform.__name__ = (
        _dataclass_transform.__qualname__
    ) = "dataclass_transform"
    globals()["dataclass_transform"] = _dataclass_transform

    _update_all("dataclass_transform")


# Function to get type name that supports generics.
_SPECIAL_NAMES = {
    Any: "Any",
    ClassVar: "ClassVar",  # noqa
    Optional: "Optional",
    Literal: "Literal",
    Final: "Final",
    Union: "Union",
    Self: "Self",
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
        if not hasattr(typ, "__forward_arg__") and type(typ).__module__ in (
            "typing",
            "typing_extensions",
            "tippo",
        ):
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


class SupportsGetItem(Protocol[_KT_contra, _VT_co]):
    """Subscritable protocol."""

    def __getitem__(self, _k):
        # type: (_KT_contra) -> _VT_co
        """
        Get value for key.

        :param _k: Key.
        :return: Value.
        """
        pass


_update_all("SupportsGetItem")


class SupportsGetSetItem(SupportsGetItem[_KT_contra, _VT_co]):
    """Settable and subscritable protocol."""

    def __setitem__(self, name, value):
        # type: (str, Any) -> None
        pass


_update_all("SupportsGetSetItem")


class SupportsGetSetDeleteItem(SupportsGetSetItem[_KT_contra, _VT_co]):
    """Settable, deletable, and subscritable protocol."""

    def __delitem__(self, name):
        # type: (str) -> None
        pass


_update_all("SupportsGetSetDeleteItem")


class SupportsKeysAndGetItem(Protocol[_KT, _VT_co]):
    """Protocol that can be used as an input to a dictionary constructor."""

    def keys(self):
        # type: () -> Iterable[_KT]
        """
        Get keys.

        :return: Keys.
        """
        pass

    def __getitem__(self, _k):
        # type: (_KT) -> _VT_co
        """
        Get value for key.

        :param _k: Key.
        :return: Value.
        """
        pass


_update_all("SupportsKeysAndGetItem")
