from __future__ import absolute_import, division, print_function

try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc  # type: ignore

import typing
import typing_extensions
import pytest

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


def test_generic_meta():
    class _Class(typing.Generic[T]):
        pass

    assert _Class[int]
    assert (_Class[int] == _Class[int]) is True
    assert (_Class[int] == _Class[(int,)]) is True
    assert (_Class[int] != _Class[(int,)]) is False

    assert isinstance(_Class[int](), _Class)
    assert isinstance(_Class[(int,)](), _Class)


def test_generic_aliases():
    for original_base, info in tippo._GENERIC_TYPES.items():
        for name in info.names:
            generic = getattr(tippo, name)
            if original_base is not generic:
                assert not hasattr(original_base, "__class_getitem__")
                assert not hasattr(type(original_base), "__getitem__")
                assert hasattr(generic, "__class_getitem__") or hasattr(type(generic), "__getitem__")


if __name__ == "__main__":
    pytest.main()
