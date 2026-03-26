# speqr

Define, validate, and certify OPC contracts for your code.

## Install

```bash
pip install speqr
```

## Quick Start

### Inline mode

```python
from speqr import contract

@contract(
    pre="input is valid",
    post="output is transformed",
    agent="transformer",
    source="raw_input",
    result="transformed_output",
)
def transform(data):
    ...
```

### Separate-doc mode

```yaml
# contracts.speq.yaml
contracts:
  - name: transform
    target: mymodule.transform
    pre: "input is valid"
    post: "output is transformed"
    roles:
      agent: transformer
      source: raw_input
      result: transformed_output
```

### Validate

```bash
speqr validate contracts.speq.yaml
```
