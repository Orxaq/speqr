# Changelog

All notable changes to speqr will be documented in this file.

## [0.1.0] — 2026-03-26

### Added
- Core types: CaseRole (7 roles), GuaranteeLevel (4-level ordering), HoareCondition
- OPCContract model with validation (all 7 roles required, conditions required)
- @contract inline decorator for annotating functions
- Speq collection model with add/get/collect
- YAML separate-doc loader (.speq.yaml format)
- Syntax validator with errors/warnings
- HTTP submission protocol for certification endpoints
- CLI: `speqr validate` (with glob support) and `speqr submit`
- Full public API exports from `speqr` top-level
- PEP 561 type marker (py.typed)

### Known Limitations
- No async submission support (planned for v0.2.0)
- No contract runtime enforcement (speqr is protocol-only)
- Certification endpoint protocol is provisional
