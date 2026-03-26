"""Tests for public API exports."""


def test_public_api_exports():
    """All key symbols are importable from speqr directly."""
    from speqr import (
        CaseRole,
        GuaranteeLevel,
        HoareCondition,
        OPCContract,
        Speq,
        contract,
        validate,
        load_speq_file,
        load_speq_string,
    )
    assert CaseRole is not None
    assert callable(contract)
    assert callable(validate)
