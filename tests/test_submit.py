"""Tests for certification submission protocol."""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from speqr.submit import submit, SubmitResult, SpeqrSubmitError
from speqr.speq import Speq
from speqr.contract import OPCContract
from speqr.types import CaseRole, HoareCondition


def _make_speq() -> Speq:
    c = OPCContract(
        name="test",
        target="mod.test",
        roles={r: r.value for r in CaseRole},
        conditions=HoareCondition(preconditions=["valid"], postconditions=["done"]),
    )
    return Speq(name="test_system", version="1.0.0", contracts=[c])


class TestSubmitResult:
    def test_passed(self):
        r = SubmitResult(passed=True, findings=[])
        assert r.passed

    def test_failed_with_findings(self):
        r = SubmitResult(passed=False, findings=[{"rule": "C-010", "message": "missing role"}])
        assert not r.passed
        assert len(r.findings) == 1


class TestSubmit:
    def test_submit_success(self):
        speq = _make_speq()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"passed": True, "findings": []}
        mock_response.raise_for_status = MagicMock()

        with patch("speqr.submit.httpx") as mock_httpx:
            mock_httpx.post.return_value = mock_response
            result = submit(speq, endpoint="https://verify.example.com/certify")

        assert result.passed
        mock_httpx.post.assert_called_once()

    def test_submit_failure_result(self):
        speq = _make_speq()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "passed": False,
            "findings": [{"rule": "C-010", "message": "incomplete"}],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("speqr.submit.httpx") as mock_httpx:
            mock_httpx.post.return_value = mock_response
            result = submit(speq, endpoint="https://verify.example.com/certify")

        assert not result.passed

    def test_submit_connection_error(self):
        speq = _make_speq()
        with patch("speqr.submit.httpx") as mock_httpx:
            mock_httpx.post.side_effect = Exception("connection refused")
            with pytest.raises(SpeqrSubmitError, match="connection"):
                submit(speq, endpoint="https://verify.example.com/certify")

    def test_submit_requires_endpoint(self):
        speq = _make_speq()
        with pytest.raises(ValueError, match="endpoint"):
            submit(speq, endpoint="")

    def test_submit_validation_failure(self):
        roles = {r: r.value for r in CaseRole}
        roles[CaseRole.AGENT] = ""
        c = OPCContract(
            name="bad",
            target="mod.bad",
            roles=roles,
            conditions=HoareCondition(preconditions=["valid"], postconditions=["done"]),
        )
        speq = Speq(name="test_system", version="1.0.0", contracts=[c])
        with pytest.raises(ValueError, match="local validation"):
            submit(speq, endpoint="https://verify.example.com/certify")
