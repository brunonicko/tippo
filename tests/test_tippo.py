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


if __name__ == "__main__":
    pytest.main()
