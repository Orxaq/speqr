# speqr

Define, validate, and certify OPC contracts for your code.

![Status: Alpha](https://img.shields.io/badge/status-alpha-orange) ![Version: v0.1.0](https://img.shields.io/badge/version-v0.1.0-blue)

## What is speqr?

speqr is a Python package for defining and validating **OPC (Obligation-Protocol-Contract)** contracts on code. A contract describes the obligations a function accepts, using **7 CaseRoles** (AGENT, PATIENT, INSTRUMENT, RESULT, SOURCE, DESTINATION, EXPERIENCER) to identify every participant in an operation. Contracts include **Hoare-style conditions** — preconditions, postconditions, and invariants — and carry a **GuaranteeLevel** that records how strongly the contract has been verified. speqr validates contract structure and can submit contracts to a certification endpoint for protocol-level auditing.

speqr is **protocol-only**: it does not enforce contracts at runtime or modify function behavior.

## Why Speqr?

Modern software development lacks a standard way to declare and verify the semantic obligations of code. Type systems tell us *what* data flows through functions, but they don't tell us *why* the function exists, *who* or *what* participates in the operation, or *what guarantees* the function makes about its behavior.

**Speqr doesn't validate your code — it validates your intent.** It provides a structured way to declare what you *mean* your code to do, who participates, and what promises you're making. This makes speqr ideal as a **code companion**: write the contract first to clarify your thinking, then write code that fulfills it.

Speqr addresses this by:

- **Making obligations explicit** — By using linguistic case roles (AGENT, PATIENT, INSTRUMENT, etc.), speqr forces you to identify every participant in an operation, clarifying not just types but *semantic intent*.
- **Recording guarantees** — Hoare conditions (pre/post/invariants) and GuaranteeLevels document the strength of your claims, from "we have tests" to "this is formally proven."
- **Enabling certification** — Because contracts are protocol-level and serializable, they can be submitted to external auditors, analyzed by static tools, or checked against organizational standards without coupling to any particular runtime or enforcement mechanism.
- **Staying out of the way** — Speqr is not a runtime contract framework. It doesn't slow down your code or change how it executes. It's pure metadata for tooling, humans, and certification systems.

Use speqr when you need a **shared language for software obligations** — whether you're documenting critical code, preparing for an audit, building safety-critical systems, or just want a disciplined way to reason about what your functions promise.

## Install

```bash
pip install speqr
```

Requires Python 3.10+.

## Complete Example: Using Speqr as a Code Companion

Here's a full workflow showing how to use speqr to clarify intent *before* writing implementation code.

### Step 1: Define the contract (intent)

```python
# user_service.py
from speqr import contract, GuaranteeLevel

@contract(
    name="create_user",
    pre="email is valid format and not already registered",
    post="user record exists in database with confirmed=False",
    invariants=["user_id is unique", "email is lowercase"],
    agent="user_service",
    patient="user_data",
    instrument="database_connection",
    result="user_record",
    source="registration_request",
    destination="user_database",
    experiencer="new_user",
    guarantee_target=GuaranteeLevel.TESTED,
)
def create_user(email: str, password: str) -> dict:
    """Create a new user account."""
    pass  # Intent is clear; now implement
```

### Step 2: Validate the contract structure

```bash
# Validate that the contract is well-formed
speqr validate user_service.py
```

Or programmatically:

```python
from speqr import validate, load_speq_file

# Load contracts from decorated functions
# (In practice, you'd extract contracts from your module)
result = validate(your_speq_object)
if not result.passed:
    print("Contract errors:", result.errors)
```

### Step 3: Implement the code

```python
@contract(
    name="create_user",
    pre="email is valid format and not already registered",
    post="user record exists in database with confirmed=False",
    invariants=["user_id is unique", "email is lowercase"],
    agent="user_service",
    patient="user_data",
    instrument="database_connection",
    result="user_record",
    source="registration_request",
    destination="user_database",
    experiencer="new_user",
    guarantee_target=GuaranteeLevel.TESTED,
)
def create_user(email: str, password: str) -> dict:
    """Create a new user account."""
    import uuid
    import hashlib
    
    # Validate precondition
    email = email.lower()
    if not _is_valid_email(email):
        raise ValueError("Invalid email format")
    if _email_exists(email):
        raise ValueError("Email already registered")
    
    # Execute operation
    user_id = str(uuid.uuid4())
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    user_record = {
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "confirmed": False,
    }
    
    # Store to destination
    _save_to_database(user_record)
    
    # Postcondition is satisfied
    return user_record
```

### Step 4: Write tests aligned with your contract

```python
# test_user_service.py
import pytest
from user_service import create_user

def test_create_user_valid_email():
    """Verify precondition: email must be valid"""
    with pytest.raises(ValueError, match="Invalid email format"):
        create_user("not-an-email", "password123")

def test_create_user_duplicate_email():
    """Verify precondition: email must not be registered"""
    create_user("user@example.com", "password123")
    with pytest.raises(ValueError, match="Email already registered"):
        create_user("user@example.com", "password456")

def test_create_user_postcondition():
    """Verify postcondition: user exists with confirmed=False"""
    result = create_user("new@example.com", "password123")
    assert result["confirmed"] is False
    assert "id" in result
    assert result["email"] == "new@example.com"

def test_create_user_invariant_lowercase():
    """Verify invariant: email is lowercase"""
    result = create_user("USER@EXAMPLE.COM", "password123")
    assert result["email"] == "user@example.com"

def test_create_user_invariant_unique_id():
    """Verify invariant: user_id is unique"""
    user1 = create_user("user1@example.com", "pass1")
    user2 = create_user("user2@example.com", "pass2")
    assert user1["id"] != user2["id"]
```

### What Just Happened?

1. **Contract first** — You declared *what* the function should do before *how*.
2. **Validation** — Speqr confirmed the contract structure is valid (all roles present, conditions specified).
3. **Implementation** — You wrote code to fulfill the obligations.
4. **Testing** — Tests verify the contract claims, justifying the `TESTED` guarantee level.

The contract didn't validate your implementation — it validated that you knew what you were trying to build. Your tests validated the implementation against the contract.

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
name: payment_contracts
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
      instrument: lookup_query
      result: is_valid
      source: account_registry
      destination: caller
      experiencer: account_holder
    guarantee_target: TESTED
```

Load and validate programmatically:

```python
from speqr import load_speq_file, validate

speq = load_speq_file("contracts.speq.yaml")
result = validate(speq)
print(result.passed, result.errors)
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

**`validate(speq: Speq) -> ValidationResult`** — Validates a Speq object. Returns `ValidationResult` with `.passed: bool` and `.errors: list[str]`.

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
- 67 tests, 99% coverage

### Planned

- Contract diffing and changelog generation
- IDE / LSP integration for inline contract hints
- Richer validation: cross-contract consistency checks
- Stable certification endpoint protocol

---

Source: [github.com/Orxaq/speqr](https://github.com/Orxaq/speqr) — License: see [LICENSE](LICENSE)
