"""Smoke test: package imports and version is set."""

import speqr


def test_version_is_set() -> None:
    assert speqr.__version__ == "0.0.1"
