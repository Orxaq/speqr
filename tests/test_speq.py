"""Tests for Speq collection model."""

import pytest
from speqr.speq import Speq
from speqr.contract import OPCContract
from speqr.types import CaseRole, HoareCondition


def _make_contract(name: str, target: str) -> OPCContract:
    return OPCContract(
        name=name,
        target=target,
        roles={r: r.value for r in CaseRole},
        conditions=HoareCondition(preconditions=["valid input"], postconditions=["valid output"]),
    )


class TestSpeq:
    def test_create_empty(self):
        s = Speq(name="my_system", version="1.0.0")
        assert len(s.contracts) == 0

    def test_add_contract(self):
        s = Speq(name="my_system", version="1.0.0")
        c = _make_contract("transform", "mod.transform")
        s = s.add(c)
        assert len(s.contracts) == 1

    def test_duplicate_name_raises(self):
        s = Speq(name="my_system", version="1.0.0")
        c1 = _make_contract("transform", "mod.transform")
        c2 = _make_contract("transform", "mod.other")
        s = s.add(c1)
        with pytest.raises(ValueError, match="duplicate"):
            s.add(c2)

    def test_get_by_name(self):
        s = Speq(name="my_system", version="1.0.0")
        c = _make_contract("transform", "mod.transform")
        s = s.add(c)
        assert s.get("transform").target == "mod.transform"

    def test_get_missing_returns_none(self):
        s = Speq(name="my_system", version="1.0.0")
        assert s.get("missing") is None

    def test_serialization_round_trip(self):
        s = Speq(name="my_system", version="1.0.0")
        s = s.add(_make_contract("a", "mod.a"))
        s = s.add(_make_contract("b", "mod.b"))
        d = s.to_dict()
        restored = Speq.from_dict(d)
        assert restored.name == s.name
        assert len(restored.contracts) == 2

    def test_collect_from_module(self):
        from speqr.contract import contract
        import types

        mod = types.ModuleType("fake_mod")
        mod.__name__ = "fake_mod"

        @contract(
            pre="x > 0", post="result > 0",
            agent="a", patient="p", instrument="i",
            result="r", source="s", destination="d", experiencer="e",
        )
        def my_func(x):
            return x

        mod.my_func = my_func
        s = Speq.collect("test_system", mod)
        assert len(s.contracts) == 1
        assert s.contracts[0].name == "my_func"
