# Speqr  /ˈspekr/

> How you declare what your code should do.

Speqr is a specification language for writing formal descriptions of software behaviour —
preconditions, postconditions, and causal assertions — that can be mechanically verified
by [Xeqer](https://github.com/Orxaq/xeqer).

## Install

```bash
pip install speqr
```

## Quick Start

```speqr
spec Divide
  input numerator: Real
  input denominator: Real
  output result: Real

  precondition denominator != 0
  postcondition result * denominator == numerator
end
```

```bash
speqr validate divide.speqr
speqr parse divide.speqr   # outputs JSON AST
```
