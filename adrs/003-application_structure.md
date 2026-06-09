# 2026-06-05 Application Structure: Layer-based

- **Decision**: Layer-based structure
- **Date**: 2026-06-05

## Alternatives considered

- Feature-based structure (vertical slices per domain)

## Rationale

- Layer-based structure is the natural starting point for a generic API template: the domains are unknown, so organizing by technical responsibility (routing, business logic, data access) is the only stable axis.
- Enforces clear dependency direction: routers call services, services call repositories, no cross-layer bypasses.
- Lower cognitive overhead when the number of domains is small -- feature slices add indirection without benefit at that scale.
- Re-evaluate toward feature-based if the app grows beyond ~5 domains, at which point the horizontal layers become harder to navigate than vertical slices.

## Rejected alternatives

- **Feature-based**: Better for large, domain-rich apps but introduces upfront structure that is speculative for a blank-slate template.

## Consequences

- Source lives under `src/app/` organized as: `routers/`, `services/`, `repositories/`, `schemas/`, `models/`, `core/`.
- Each layer has strict "must not contain" rules -- see [standards/structure.md](../standards/structure.md).
- When a domain grows complex enough that its layer files dwarf all others, that is the signal to extract it into a feature slice.
