"""Load speq files (YAML separate-doc format)."""

from __future__ import annotations

from pathlib import Path

import yaml

from speqr.contract import OPCContract
from speqr.speq import Speq
from speqr.types import CaseRole, GuaranteeLevel, HoareCondition


def load_speq_string(content: str) -> Speq:
    """Parse a YAML string into a Speq."""
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"invalid YAML: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("speq file must be a YAML mapping")
    if "name" not in data:
        raise ValueError("speq file must have a 'name' field")

    contracts = []
    for raw in data.get("contracts", []):
        roles = {CaseRole(k): v for k, v in raw.get("roles", {}).items()}
        pre = raw.get("pre", "")
        post = raw.get("post", "")
        invariants = raw.get("invariants", "")
        conditions = HoareCondition(
            preconditions=[pre] if isinstance(pre, str) and pre else pre if isinstance(pre, list) else [],
            postconditions=[post] if isinstance(post, str) and post else post if isinstance(post, list) else [],
            invariants=[invariants] if isinstance(invariants, str) and invariants else invariants if isinstance(invariants, list) else [],
        )
        gt_raw = raw.get("guarantee_target")
        if gt_raw is not None:
            gt_match = next(
                (g for g in GuaranteeLevel if g.label == gt_raw.lower()),
                None,
            )
            if gt_match is None:
                raise ValueError(f"unknown guarantee_target: {gt_raw}")
            guarantee_target = gt_match
        else:
            guarantee_target = GuaranteeLevel.TESTED

        contracts.append(
            OPCContract(
                name=raw["name"],
                target=raw["target"],
                roles=roles,
                conditions=conditions,
                guarantee_target=guarantee_target,
                version=raw.get("version", "1"),
                tags=raw.get("tags", []),
            )
        )

    return Speq(
        name=data["name"],
        version=data.get("version", "0.1.0"),
        contracts=contracts,
    )


def load_speq_file(path: Path | str) -> Speq:
    """Load a speq from a YAML file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"speq file not found: {path}")
    content = path.read_text()
    return load_speq_string(content)
