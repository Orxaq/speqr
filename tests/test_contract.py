"""Tests for OPCContract model."""

import pytest
from speqr.contract import OPCContract
from speqr.types import CaseRole, GuaranteeLevel, HoareCondition


class TestOPCContract:
    def test_create_minimal_contract(self):
        c = OPCContract(
            name="transform",
            target="mymodule.transform",
            roles={
                CaseRole.AGENT: "transformer",
                CaseRole.PATIENT: "data",
                CaseRole.INSTRUMENT: "algorithm",
                CaseRole.RESULT: "output",
                CaseRole.SOURCE: "raw_input",
                CaseRole.DESTINATION: "data_store",
                CaseRole.EXPERIENCER: "operator",
            },
            conditions=HoareCondition(
                preconditions=["input is valid"],
                postconditions=["output is transformed"],
            ),
        )
        assert c.name == "transform"
        assert len(c.roles) == 7

    def test_missing_roles_raises(self):
        with pytest.raises(ValueError, match="missing.*role"):
            OPCContract(
                name="bad",
                target="mymodule.bad",
                roles={CaseRole.AGENT: "a"},
                conditions=HoareCondition(preconditions=["x"]),
            )

    def test_empty_conditions_raises(self):
        all_roles = {r: r.value for r in CaseRole}
        with pytest.raises(ValueError, match="condition"):
            OPCContract(
                name="bad",
                target="mymodule.bad",
                roles=all_roles,
                conditions=HoareCondition(),
            )

    def test_serialization_round_trip(self):
        all_roles = {r: r.value for r in CaseRole}
        c = OPCContract(
            name="transform",
            target="mymodule.transform",
            roles=all_roles,
            conditions=HoareCondition(
                preconditions=["input is valid"],
                postconditions=["output is transformed"],
            ),
        )
        d = c.to_dict()
        restored = OPCContract.from_dict(d)
        assert restored.name == c.name
        assert restored.roles == c.roles

    def test_to_yaml_and_back(self):
        all_roles = {r: r.value for r in CaseRole}
        c = OPCContract(
            name="transform",
            target="mymodule.transform",
            roles=all_roles,
            conditions=HoareCondition(
                preconditions=["input is valid"],
                postconditions=["output is transformed"],
            ),
        )
        yaml_str = c.to_yaml()
        assert "transform" in yaml_str
        restored = OPCContract.from_yaml(yaml_str)
        assert restored.name == c.name


class TestContractDecorator:
    def test_decorator_attaches_contract(self):
        from speqr.contract import contract

        @contract(
            pre="x > 0",
            post="result >= 0",
            agent="compute_engine",
            patient="input_data",
            instrument="algorithm",
            result="output_data",
            source="data_source",
            destination="data_sink",
            experiencer="operator",
        )
        def my_func(x):
            return x * 2

        assert hasattr(my_func, "__speqr_contract__")
        assert my_func.__speqr_contract__.name == "my_func"
        assert my_func(5) == 10

    def test_decorator_with_custom_name(self):
        from speqr.contract import contract

        @contract(
            name="custom_name",
            pre="x > 0",
            post="result >= 0",
            agent="a", patient="p", instrument="i",
            result="r", source="s", destination="d", experiencer="e",
        )
        def my_func(x):
            return x

        assert my_func.__speqr_contract__.name == "custom_name"
