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
                assert hasattr(generic, "__class_getitem__")
                assert hasattr(generic, "__parameters__")
                assert generic.__parameters__ == info.vars


if __name__ == "__main__":
    pytest.main()
