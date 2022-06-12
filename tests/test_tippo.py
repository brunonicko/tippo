import typing

import typing_extensions
import pytest

import tippo


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
                assert not tippo.is_generic(original_base)
                assert tippo.is_generic(generic)
                assert hasattr(generic, "__class_getitem__")


if __name__ == "__main__":
    pytest.main()
