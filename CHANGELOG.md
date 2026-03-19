# Changelog

All notable changes to Speqr are documented here.
Format: [version] YYYY-MM-DD — description. Refs: SR11-7(2011)-§ or N/A.

## [0.1.0] 2026-03-19
Req: SR11-7(2011)-§model-development

Initial release. Speqr specification language v0.1.0.

### Added
- VariableType enum (Int/Real/Bool/String/List/Set/Map) with SUMO grounding
- AST nodes: SpecNode, InputNode, OutputNode, PreconditionNode,
  PostconditionNode, CausalAssertionNode, SpecRefNode
- PEG grammar (grammar.lark) — normative spec definition
- Parser: Speqr source → SpecNode AST
- Validator: type-check expressions + detect reference cycles
- Serializer: SpecNode ↔ JSON AST (inter-package contract with Xeqer)
- CLI: `speqr parse <file>` (JSON AST), `speqr validate <file>` (exit 0/1)

### Excludes (future releases)
- IDE integration
- Python/TypeScript code binding
- Domain types (CreditScore, InterestRate — deferred to Qennix)

## Unreleased
