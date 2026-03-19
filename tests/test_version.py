"""Smoke test: package imports and version is set."""

import speqr


def test_version_is_set() -> None:
    assert speqr.__version__ == "0.1.0"


def test_public_api_exports() -> None:
    assert callable(speqr.parse)
    assert callable(speqr.validate)
    assert callable(speqr.to_json)
    assert callable(speqr.from_json)
