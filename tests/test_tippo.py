from __future__ import absolute_import, division, print_function

try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc  # type: ignore

import typing

import pytest
import six
import typing_extensions

import tippo

T = tippo.TypeVar("T")


def test_all():
    assert tippo._all_ is getattr(tippo, "__all__")

    assert set(typing.__all__).issubset(tippo._all_)  # type: ignore
    assert set(typing_extensions.__all__).issubset(tippo._all_)  # type: ignore

    for member in tippo._all_:
        assert not member.startswith("_")
        assert hasattr(tippo, member)

    if "GenericMeta" in typing.__all__:  # type: ignore
        assert "GenericMeta" in tippo._all_

    for _b, (names, _v) in tippo._GENERIC_TYPES.items():
        for name in names:
            assert name in tippo._all_

    assert "final" in tippo._all_
    assert "TypeAlias" in tippo._all_
    assert "ClassVar" in tippo._all_
    assert "get_origin" in tippo._all_
    assert "get_args" in tippo._all_
    assert "get_name" in tippo._all_


def test_missing():
    obj = object()
    for missing in ("TypeAlias", "ClassVar"):
        if not hasattr(typing, missing) and not hasattr(typing_extensions, missing):
            assert getattr(tippo, missing)[obj] is obj


def test_new_type():
    if not hasattr(typing, "NewType") and not hasattr(typing_extensions, "NewType"):
        obj = object()
        assert getattr(tippo, "NewType")("obj", obj) is obj


def test_generic_meta():

    # Metaclass uniformity.
    assert isinstance(tippo.Generic, tippo.GenericMeta)

    # Comparisons.
    assert tippo.Mapping[str, int] == tippo.Mapping[str, int]
    assert not (tippo.Mapping[str, int] != tippo.Mapping[str, int])

    # Bracket syntax should not work if class doesn't inherit from Generic.
    class Class(six.with_metaclass(tippo.GenericMeta, object)):
        pass

    with pytest.raises(TypeError):
        _BadClass = Class[None]  # type: ignore
        assert not _BadClass

    # Should error if didn't specify type variables to Generic.
    with pytest.raises(TypeError):

        class _BadClass(Class, tippo.Generic[3]):  # type: ignore
            pass

        assert not _BadClass

    with pytest.raises(TypeError):

        class _BadClass(Class, tippo.Generic[int]):  # type: ignore
            pass

        assert not _BadClass

    # Declare a proper Generic class and check inheritance, equality, and instantiation.
    class _Class(Class, tippo.Generic[T]):
        pass

    assert _Class[int]
    assert (_Class[int] == _Class[int]) is True
    assert (_Class[int] == _Class[(int,)]) is True
    assert (_Class[int] != _Class[(int,)]) is False

    assert isinstance(_Class[int](), _Class)
    assert isinstance(_Class[(int,)](), _Class)

    assert issubclass(_Class, Class)
    assert _Class[int]
    assert (_Class[int] == _Class[int]) is True
    assert (_Class[int] == _Class[(int,)]) is True
    assert (_Class[int] != _Class[(int,)]) is False

    assert isinstance(_Class[int](), _Class)
    assert isinstance(
        _Class[(int,)](),
        _Class,
    )

    # Test weakref slot with generic.
    class Class(tippo.Generic[T]):
        __slots__ = ("__weakref__",)

    class SubClass(Class[T]):
        __slots__ = ()

    assert SubClass


def test_generic_aliases():
    for original_base, info in tippo._GENERIC_TYPES.items():
        for name in info.names:
            generic = getattr(tippo, name)
            if original_base is not generic:
                assert not hasattr(original_base, "__class_getitem__")
                assert not hasattr(type(original_base), "__getitem__")
                assert hasattr(generic, "__class_getitem__") or hasattr(type(generic), "__getitem__")


def test_get_origin():
    assert tippo.get_origin(tippo.Literal[42]) is tippo.Literal
    assert tippo.get_origin(int) is None
    assert tippo.get_origin(tippo.ClassVar[int]) is tippo.ClassVar
    assert tippo.get_origin(tippo.Generic) is tippo.Generic
    assert tippo.get_origin(tippo.Generic[T]) is tippo.Generic
    assert tippo.get_origin(tippo.Union[T, int]) is tippo.Union
    assert tippo.get_origin(tippo.List[tippo.Tuple[T, T]][int]) in (list, tippo.List)

    assert tippo.get_origin(tippo.Callable) in (tippo.Callable, collections_abc.Callable)
    assert tippo.get_origin(tippo.Tuple) in (tippo.Tuple, tuple)
    assert tippo.get_origin(tippo.Dict) in (tippo.Dict, dict)
    assert tippo.get_origin(tippo.List) in (tippo.List, list)
    assert tippo.get_origin(tippo.Set) in (tippo.Set, set)
    assert tippo.get_origin(tippo.Union) is None
    assert tippo.get_origin(tippo.Literal) is None
    assert tippo.get_origin(tippo.Final) is None
    assert tippo.get_origin(tippo.ClassVar) is None

    assert tippo.get_origin(tippo.Literal[42]) is tippo.Literal
    assert tippo.get_origin(int) is None
    assert tippo.get_origin(None) is None
    assert tippo.get_origin(tippo.ClassVar[int]) is tippo.ClassVar
    assert tippo.get_origin(tippo.Generic) is tippo.Generic
    assert tippo.get_origin(tippo.Generic[T]) is tippo.Generic
    assert tippo.get_origin(tippo.Union[T, int]) is tippo.Union
    assert tippo.get_origin(tippo.List[tippo.Tuple[T, T]][int]) in (tippo.List, list)
    assert tippo.get_origin(tippo.Callable[[str, int], bool]) in (tippo.Callable, collections_abc.Callable)
    assert tippo.get_origin(tippo.Tuple[str]) in (tippo.Tuple, tuple)
    assert tippo.get_origin(tippo.Dict[str, int]) in (tippo.Dict, dict)
    assert tippo.get_origin(tippo.List[str]) in (tippo.List, list)
    assert tippo.get_origin(tippo.Set[str]) in (tippo.Set, set)
    assert tippo.get_origin(tippo.Union[str, int]) is tippo.Union
    assert tippo.get_origin(tippo.Literal[True, 0]) is tippo.Literal
    assert tippo.get_origin(tippo.Final[int]) is tippo.Final
    assert tippo.get_origin(tippo.ClassVar[int]) is tippo.ClassVar


def test_get_args():
    assert tippo.get_args(tippo.Dict[str, int]) == (str, int)
    assert tippo.get_args(int) == ()
    assert tippo.get_args(tippo.Union[int, tippo.Union[T, int], str][int]) == (int, str)
    assert tippo.get_args(tippo.Union[int, tippo.Tuple[T, int]][str]) == (int, tippo.Tuple[str, int])
    assert tippo.get_args(tippo.Callable[[], T][int]) == ([], int)

    assert tippo.get_args(tippo.Dict) == ()
    assert tippo.get_args(int) == ()
    assert tippo.get_args(None) == ()
    assert tippo.get_args(tippo.Union) == ()
    assert tippo.get_args(tippo.Callable) == ()

    assert tippo.get_args(tippo.Dict[str, int]) == (str, int)
    assert tippo.get_args(tippo.Union[int, tippo.Union[T, int], str][int]) == (int, str)
    assert tippo.get_args(tippo.Union[int, tippo.Tuple[T, int]][str]) == (int, tippo.Tuple[str, int])
    assert tippo.get_args(tippo.Callable[[float, bool], T][int]) == ([float, bool], int)
    assert tippo.get_args(tippo.Callable[[], T][int]) == ([], int)
    assert tippo.get_args(tippo.Callable[Ellipsis, T][int]) == (Ellipsis, int)

    assert tippo.get_args(tippo.Union[int, tippo.Tuple[T, tippo.Dict[str, bool]]][bool]) == (
        int,
        tippo.Tuple[bool, tippo.Dict[str, bool]],
    )
    assert tippo.get_args(tippo.Dict[str, T][bool]) == (str, bool)
    assert tippo.get_args(tippo.List[T][bool]) == (bool,)
    assert tippo.get_args(tippo.Set[T][bool]) == (bool,)

    assert tippo.get_args(tippo.Union[int, tippo.Union[T, int], str]) == (int, T, str)
    assert tippo.get_args(tippo.Union[int, tippo.Tuple[T, int]]) == (int, tippo.Tuple[T, int])
    assert tippo.get_args(tippo.Callable[[float, bool], T]) == ([float, bool], T)
    assert tippo.get_args(tippo.Callable[[], T]) == ([], T)
    assert tippo.get_args(tippo.Callable[Ellipsis, T]) == (Ellipsis, T)


def test_get_name():
    assert tippo.get_name(None) == "None"
    assert tippo.get_name(Ellipsis) == "..."
    assert tippo.get_name(None) == "None"
    assert tippo.get_name(type(None)) == "NoneType"
    assert tippo.get_name(int) == "int"
    assert tippo.get_name(True) == "True"
    assert tippo.get_name(False) == "False"
    assert tippo.get_name(NotImplemented) == "NotImplemented"
    assert tippo.get_name(type(NotImplemented)) == "NotImplementedType"
    assert tippo.get_name(tippo.Any) == "Any"
    assert tippo.get_name(tippo.Optional) == "Optional"
    assert tippo.get_name(tippo.Generic) == "Generic"
    assert tippo.get_name(tippo.Literal) == "Literal"
    assert tippo.get_name(tippo.Final) == "Final"
    assert tippo.get_name(tippo.ForwardRef) == "ForwardRef"
    assert tippo.get_name(tippo.ClassVar) == "ClassVar"
    assert tippo.get_name(tippo.Callable) == "Callable"
    assert tippo.get_name(tippo.Tuple) == "Tuple"
    assert tippo.get_name(tippo.Union) == "Union"
    assert tippo.get_name(tippo.Mapping) == "Mapping"
    assert tippo.get_name(tippo.Union) == "Union"
    assert tippo.get_name(tippo.List) == "List"
    assert tippo.get_name(tippo.Dict) == "Dict"
    assert tippo.get_name(tippo.Set) == "Set"

    assert tippo.get_name(tippo.ForwardRef("Foo")) == "Foo"
    assert tippo.get_name(tippo.Generic[T]) == "Generic"
    assert tippo.get_name(tippo.Literal[True, False, "abc"]) == "Literal"
    assert tippo.get_name(tippo.Final[int]) == "Final"
    assert tippo.get_name(tippo.ClassVar[int]) == "ClassVar"
    assert tippo.get_name(tippo.Callable[[str, int], bool]) == "Callable"
    assert tippo.get_name(tippo.Callable[..., bool]) == "Callable"
    assert tippo.get_name(tippo.Tuple[str, int]) == "Tuple"
    assert tippo.get_name(tippo.Tuple[str, ...]) == "Tuple"
    assert tippo.get_name(tippo.Union[str, int]) == "Union"
    assert tippo.get_name(tippo.Mapping[str, int]) == "Mapping"
    assert tippo.get_name(tippo.Union[str, int]) == "Union"
    assert tippo.get_name(tippo.List[str]) == "List"
    assert tippo.get_name(tippo.Dict[str, int]) == "Dict"
    assert tippo.get_name(tippo.Set[str]) == "Set"
    assert tippo.get_name(tippo.Set["Foo"]) == "Set"
    assert tippo.get_name(tippo.List["Tuple"]) == "List"

    assert tippo.get_name(object()) is None


if __name__ == "__main__":
    pytest.main()
