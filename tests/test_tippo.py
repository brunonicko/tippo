from __future__ import absolute_import, division, print_function

import typing
import typing_extensions
import pytest

import tippo


T = tippo.TypeVar("T")


def test_imports():
    for member in getattr(typing, "__all__") + getattr(typing_extensions, "__all__"):
        if member.startswith("_"):
            continue
        assert hasattr(tippo, member)


def test_generic_aliases():
    for original_base, info in tippo._GENERIC_TYPES.items():
        for name in info.names:
            generic = getattr(tippo, name)
            if original_base is not generic:
                assert not hasattr(original_base, "__class_getitem__")
                assert not hasattr(type(original_base), "__getitem__")
                assert hasattr(generic, "__class_getitem__") or hasattr(type(generic), "__getitem__")


def test_generic_meta():
    class _Class(typing.Generic[T]):
        pass

    assert _Class[int]
    assert (_Class[int] == _Class[int]) is True
    assert (_Class[int] == _Class[(int,)]) is True
    assert (_Class[int] != _Class[(int,)]) is False

    assert isinstance(_Class[int](), _Class)
    assert isinstance(_Class[(int,)](), _Class)


def test_get_name():
    assert tippo.get_name(None) == "None"
    assert tippo.get_name(Ellipsis) == "..."
    assert tippo.get_name(None) == "None"
    assert tippo.get_name(type(None)) == "NoneType"
    assert tippo.get_name(True) == "True"
    assert tippo.get_name(False) == "False"
    assert tippo.get_name(NotImplemented) == "NotImplemented"
    assert tippo.get_name(type(NotImplemented)) == "NotImplementedType"
    assert tippo.get_name(tippo.Literal) == "Literal"
    assert tippo.get_name(tippo.Final) == "Final"
    assert tippo.get_name(tippo.ClassVar) == "ClassVar"
    assert tippo.get_name(tippo.Callable) == "Callable"
    assert tippo.get_name(tippo.Tuple) == "Tuple"
    assert tippo.get_name(tippo.Union) == "Union"
    assert tippo.get_name(tippo.Mapping) == "Mapping"
    assert tippo.get_name(tippo.Union) == "Union"
    assert tippo.get_name(tippo.List) == "List"
    assert tippo.get_name(tippo.Dict) == "Dict"
    assert tippo.get_name(tippo.Set) == "Set"


def test_get_path():
    assert tippo.get_path(tippo.Literal[True, False, "abc"]) == "tippo.Literal[True, False, abc]"
    assert tippo.get_path(tippo.Final[int]) == "tippo.Final[int]"
    assert tippo.get_path(tippo.ClassVar[int]) == "tippo.ClassVar[int]"
    assert tippo.get_path(tippo.Callable[[str, int], bool]) == "tippo.Callable[[str, int], bool]"
    assert tippo.get_path(tippo.Callable[..., bool]) == "tippo.Callable[..., bool]"
    assert tippo.get_path(tippo.Tuple[str, int]) == "tippo.Tuple[str, int]"
    assert tippo.get_path(tippo.Tuple[str, ...]) == "tippo.Tuple[str, ...]"
    assert tippo.get_path(tippo.Union[str, int]) == "tippo.Union[str, int]"
    assert tippo.get_path(tippo.Mapping[str, int]) == "tippo.Mapping[str, int]"
    assert tippo.get_path(tippo.Union[str, int]) == "tippo.Union[str, int]"
    assert tippo.get_path(tippo.List[str]) == "tippo.List[str]"
    assert tippo.get_path(tippo.Dict[str, int]) == "tippo.Dict[str, int]"
    assert tippo.get_path(tippo.Set[str]) == "tippo.Set[str]"


if __name__ == "__main__":
    pytest.main()
