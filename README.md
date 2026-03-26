# speqr

Define, validate, and certify OPC contracts for your code.

![Status: Alpha](https://img.shields.io/badge/status-alpha-orange) ![Version: v0.1.0](https://img.shields.io/badge/version-v0.1.0-blue)

## What is speqr?

speqr is a Python package for defining and validating **OPC (Obligation-Protocol-Contract)** contracts on code. A contract describes the obligations a function accepts, using **7 CaseRoles** (AGENT, PATIENT, INSTRUMENT, RESULT, SOURCE, DESTINATION, EXPERIENCER) to identify every participant in an operation. Contracts include **Hoare-style conditions** — preconditions, postconditions, and invariants — and carry a **GuaranteeLevel** that records how strongly the contract has been verified. speqr validates contract structure and can submit contracts to a certification endpoint for protocol-level auditing.

speqr is **protocol-only**: it does not enforce contracts at runtime or modify function behavior.

## Install

```bash
pip install speqr
```

Requires Python 3.10+.

## Quick Start: Inline Mode

Attach a contract to a function using the `@contract` decorator. All 7 CaseRoles are available as keyword arguments.

```python
from speqr import contract, GuaranteeLevel

@contract(
    name="transfer_funds",
    pre="source account has sufficient balance",
    post="destination account balance increased by amount",
    invariants=["total funds conserved", "no account balance goes negative"],
    agent="payment_service",
    patient="amount",
    instrument="transaction_record",
    result="updated_balances",
    source="source_account",
    destination="destination_account",
    experiencer="account_holder",
    guarantee_target=GuaranteeLevel.TESTED,
)
def transfer_funds(source_account, destination_account, amount):
    ...
```

The decorator is a no-op at runtime — it attaches contract metadata to the function for validation and certification tooling.

## Quick Start: YAML Mode

Define contracts in a `.speq.yaml` file, separate from your source code.

```yaml
# contracts.speq.yaml
speq: payment_contracts
version: "1.0"
contracts:
  - name: transfer_funds
    target: mypackage.payments.transfer_funds
    pre: "source account has sufficient balance"
    post: "destination account balance increased by amount"
    invariants:
      - "total funds conserved"
      - "no account balance goes negative"
    roles:
      agent: payment_service
      patient: amount
      instrument: transaction_record
      result: updated_balances
      source: source_account
      destination: destination_account
      experiencer: account_holder
    guarantee_target: TESTED

  - name: validate_account
    target: mypackage.payments.validate_account
    pre: "account_id is a non-empty string"
    post: "returns True if account exists and is active"
    roles:
      agent: validation_service
      patient: account_id
      result: is_valid
      source: account_registry
```

Load and validate programmatically:

```python
from speqr import load_speq_file, validate

speq = load_speq_file("contracts.speq.yaml")
result = validate(speq)
print(result.valid, result.errors)
```

## CLI

### Validate speq files

```bash
speqr validate contracts.speq.yaml
speqr validate src/contracts/
```

Validates the contract structure of one or more `.speq.yaml` files (or all `.speq.yaml` files under a directory). Exits non-zero if any contract is invalid.

### Submit for certification

```bash
speqr submit contracts.speq.yaml --endpoint https://certify.example.com/api/v1
```

Submits a speq file to a certification endpoint. The certification protocol is provisional; see the endpoint documentation for authentication and response format.

## Key Concepts

| Concept | Description |
|---|---|
| **OPCContract** | A single contract: one function's obligations, roles, and conditions |
| **Speq** | A named collection of OPC contracts (one `.speq.yaml` file = one Speq) |
| **CaseRole** | One of 7 semantic roles describing participants: AGENT, PATIENT, INSTRUMENT, RESULT, SOURCE, DESTINATION, EXPERIENCER |
| **HoareCondition** | A pre, post, or invariant condition expressed as a natural-language or formal string |
| **GuaranteeLevel** | Assurance level: `TESTED` < `BOUNDED` < `VERIFIED` < `PROVEN` |

### CaseRoles

| Role | Meaning |
|---|---|
| `AGENT` | The entity that performs the action |
| `PATIENT` | The entity that is acted upon |
| `INSTRUMENT` | The means or mechanism used |
| `RESULT` | The entity produced or returned |
| `SOURCE` | Where something comes from |
| `DESTINATION` | Where something goes to |
| `EXPERIENCER` | The entity that receives or observes the outcome |

### GuaranteeLevel

| Level | Meaning |
|---|---|
| `TESTED` | Contract is covered by tests |
| `BOUNDED` | Behavior is bounded by analysis |
| `VERIFIED` | Formally verified against a model |
| `PROVEN` | Mathematically proven |

## API Reference

All public names are importable from `speqr`:

```python
from speqr import (
    # Core types
    CaseRole,
    GuaranteeLevel,
    HoareCondition,
    OPCContract,
    Speq,

    # Decorator (inline mode)
    contract,

    # Validation
    validate,
    ValidationResult,

    # Loading
    load_speq_file,
    load_speq_string,

    # Submission
    submit,
    SubmitResult,
    SpeqrSubmitError,
)
```

**`contract(**kwargs)`** — Decorator. Attaches a contract to a function. No runtime effect.

**`validate(speq: Speq) -> ValidationResult`** — Validates a Speq object. Returns `ValidationResult` with `.valid: bool` and `.errors: list[str]`.

**`load_speq_file(path: str | Path) -> Speq`** — Parses a `.speq.yaml` file and returns a `Speq`.

**`load_speq_string(text: str) -> Speq`** — Parses a YAML string and returns a `Speq`.

**`submit(speq: Speq, endpoint: str, **kwargs) -> SubmitResult`** — Submits a Speq to a certification endpoint. Raises `SpeqrSubmitError` on failure.

## Status

**v0.1.0 — Alpha**

### What works

- `@contract` decorator (inline mode)
- `.speq.yaml` loading and parsing (`load_speq_file`, `load_speq_string`)
- Contract validation (`validate`, `ValidationResult`)
- CLI: `speqr validate`
- CLI: `speqr submit`
- All 7 CaseRoles, 4 GuaranteeLevels, Hoare conditions
- 51 tests, 88% coverage

### Planned

- Contract diffing and changelog generation
- IDE / LSP integration for inline contract hints
- Richer validation: cross-contract consistency checks
- Stable certification endpoint protocol

---

Source: [github.com/Orxaq/speqr](https://github.com/Orxaq/speqr) — License: see [LICENSE](LICENSE)
