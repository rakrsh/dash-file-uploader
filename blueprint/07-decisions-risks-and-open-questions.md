# Architecture Decisions, Risks, and Open Questions

## 1. Decision status

This is an initial decision register. “Proposed” is not approval. The project owner should accept, revise, or supersede each decision before implementation work depends on it.

## 2. Initial architecture decision records

### ADR-001 — App-scoped configuration

- **Status:** Proposed; required.
- **Decision:** Store uploader configuration on an app-scoped extension/config object or equivalent closure, not in mutable module-global settings.
- **Reason:** Both reference projects use shared settings that can cause interference when more than one Dash app is configured in one process.
- **Consequence:** Component factories and route registration must receive or resolve the correct app-scoped configuration. Add two-app isolation tests.

### ADR-002 — Server-generated storage identifiers

- **Status:** Proposed; required.
- **Decision:** Generate opaque session references and storage keys on the server. Treat original filenames as metadata only.
- **Reason:** The legacy handler uses request-derived path components; the Uppy handler sanitizes names but still derives destination names from the request.
- **Consequence:** The API must maintain a server-side mapping from session/reference to owner, state, and storage key. Applications should not rely on original filenames as unique identifiers.

### ADR-003 — Authorization remains host-app-owned but is mandatory

- **Status:** Proposed; requires API design.
- **Decision:** The host application supplies identity and authorization policy; the library invokes that policy for all session lifecycle operations.
- **Reason:** A reusable Dash package cannot safely invent each application's user/tenant model, but a default unauthenticated upload route is not an acceptable implicit policy.
- **Consequence:** The integration contract must specify how request identity is obtained and how denial is represented. Anonymous mode, if ever supported, needs explicit quotas and threat review.

### ADR-004 — Transport protocol

- **Status:** Open; blocks production implementation.
- **Options:** single multipart request; resumable protocol/service; direct-to-object-storage multipart; a deliberately designed application chunk API.
- **Decision criteria:** maximum file size, restart/resume need, proxy limits, multi-worker deployment, storage backend, operating burden, and integrity requirements.
- **Proposed direction:** prefer a mature protocol/service where resumability is required; avoid recreating a custom chunk protocol without a demonstrated need. If the simplest multipart mode is chosen, explicitly accept and document its size/restart limits.
- **Consequence:** Uppy plugin, backend routes, deployment diagram, persistence needs, tests, and operational responsibilities depend on this decision.

### ADR-005 — Storage backend and staging

- **Status:** Open; choose one first-release profile.
- **Options:** local/shared filesystem; object storage; dedicated upload service.
- **Decision criteria:** deployment target, shared-worker topology, file size, storage cost, atomicity, retention, and operator expertise.
- **Proposed invariant:** staging is private and server-keyed; final visibility occurs only after verified completion.

### ADR-006 — Durable session state

- **Status:** Open; must match deployment topology.
- **Options:** database-backed state; a durable service-specific session store; limited in-process state only for an explicitly single-process development mode.
- **Proposed invariant:** session owner, expiry, and completion state must not be inferred from browser props or a single worker's memory.

### ADR-007 — Dash completion contract

- **Status:** Proposed.
- **Decision:** Distinguish action receipt from eventual upload result. Callback payload contains an opaque server-confirmed file reference and safe metadata, not a trusted path or client-asserted completion.
- **Reason:** The Uppy5 project has trigger/status props and documents receipt-versus-outcome semantics; preserving that distinction avoids ambiguous callbacks.
- **Consequence:** Define event ordering, batch semantics, and whether callbacks fire per file or per batch.

### ADR-008 — UI toolkit

- **Status:** Open.
- **Options:** Uppy Dashboard; smaller custom component; native Dash upload components plus server API.
- **Decision criteria:** accessibility, customization, package size, supported React/Dash versions, plugin support, and maintenance capacity.
- **Proposed direction:** reuse Uppy if its UX meets requirements, but keep protocol and authorization independent from Uppy. Avoid presenting Uppy restrictions as server security controls.

### ADR-009 — Supported runtime matrix

- **Status:** Open.
- **Decision:** Set the minimum supported Python/Dash/Node/browser versions from user requirements and CI capacity, not from the newest available release alone.
- **Reason:** The Uppy5 reference currently declares Python `>=3.13` and Dash `>=3.4.0`, while the legacy package has old and broad lower bounds. Neither range automatically meets this project's audience.

### ADR-010 — Build artifacts and locks

- **Status:** Proposed.
- **Decision:** Commit one lockfile per package ecosystem and define one source of truth for generated Dash bindings/bundles. CI must build and install from a clean checkout.
- **Consequence:** Document generated-file policy and verify built package contents before publishing.

## 3. Risk register

| ID | Risk | Likelihood / impact | Mitigation / owner action |
|---|---|---|---|
| **R-01** | Transport/storage requirements remain undecided and cause architectural rework. | High / High | Resolve ADR-004/005 before backend implementation. |
| **R-02** | “No issues” is interpreted as a guarantee that cannot be made. | High / High | Define measurable security/reliability controls and release gates; communicate residual risk and scope. |
| **R-03** | Host application auth integration is underspecified, leading to an open upload route. | Medium / Critical | Make auth policy mandatory for production configuration; test every lifecycle operation. |
| **R-04** | Resource limits are too generous or inconsistent with proxy/storage limits. | Medium / High | Set numeric defaults from deployment requirements; validate in app and proxy; load-test. |
| **R-05** | A custom resumable protocol introduces race/corruption bugs. | Medium / High | Prefer a mature protocol where suitable; if custom, write protocol spec and adversarial/concurrency tests first. |
| **R-06** | Multi-worker deployment loses session state or cannot access staging data. | Medium / High | Choose durable shared state/storage or limit support explicitly; test the declared topology. |
| **R-07** | Legacy compatibility pressures weaken the new security contract. | Medium / High | Keep compatibility adapter optional and fail closed; provide a migration guide instead of insecure implicit behavior. |
| **R-08** | New project lacks maintainers for ongoing dependencies and security response. | Medium / High | Confirm owner, security contact, release cadence, and support policy before launch. |
| **R-09** | Generated artifacts or dependencies make releases non-reproducible. | Medium / Medium | Lock dependencies; clean-build/package tests in CI; verify artifact contents. |
| **R-10** | Test suite covers only happy-path UI flows. | Medium / High | Make protocol, security, failure, concurrency, and packaging tests required gates. |
| **R-11** | Performance claims do not match production topology. | Medium / Medium | Publish reproducible benchmark parameters and measured envelope; avoid unqualified “unlimited” claims. |

## 4. Open questions for the project owner

These should be answered before finalizing the requirements and implementation plan:

1. What exact PyPI/GitHub name and organization should own the new project?
2. Is backward compatibility with either existing package required, or is a clean API acceptable?
3. Who are the expected users: internal authenticated apps, customer-facing authenticated apps, or public uploads?
4. What maximum file size, concurrent uploads, files per batch, and per-user storage quota must be supported?
5. Must uploads resume after browser reload, process restart, or network interruption?
6. Which deployment is required first: one Flask/Dash service, multiple workers, a dedicated uploader, or direct object storage?
7. Which storage backends are required at launch?
8. What identity/authorization API can the host app provide?
9. What data retention, deletion, backup, and scanning policy applies?
10. Which Python/Dash/browser versions are mandatory?
11. Is a rich Uppy Dashboard required, or can a lighter/native UI meet the product goal?
12. Who will own maintenance and respond to security reports?

## 5. Decision review cadence

Revisit this register:

- before implementation of the upload protocol;
- before adding a storage backend or authentication mode;
- when changing the supported runtime matrix;
- before beta and stable release;
- after any incident, threat-model finding, or major upstream dependency change.

Record accepted decisions with date, owner, rationale, alternatives considered, and consequences. Superseded decisions should remain linked rather than silently erased.
