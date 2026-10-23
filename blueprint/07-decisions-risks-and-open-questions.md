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

- **Status:** Accepted 2026-10-23; integration API design remains open.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Require an authenticated host application for first-release uploads; exclude anonymous/public uploads. The host application supplies verified identity and authorization policy, and the package invokes that policy for every lifecycle operation and completion-reference access.
- **Reason:** A reusable Dash package cannot safely invent each application's user/tenant model, and an unauthenticated upload route is not an acceptable implicit policy.
- **Consequences:** The integration contract must specify how request identity is obtained and how denial is represented. The host remains responsible for authentication and authorization decisions.

### ADR-004 — Transport protocol

- **Status:** Open; blocks production implementation.
- **Options:** single multipart request; resumable protocol/service; direct-to-object-storage multipart; a deliberately designed application chunk API.
- **Decision criteria:** maximum file size, restart/resume need, proxy limits, multi-worker deployment, storage backend, operating burden, and integrity requirements.
- **Accepted requirement:** Uploads must resume after network interruption, browser reload, application/process restart, and requests reaching a different worker.
- **Proposed direction:** Given the accepted resume requirement, prefer a mature resumable protocol/service; avoid recreating a custom chunk protocol without a demonstrated need. Validate the choice against actual file-size and proxy limits before approval.
- **Consequence:** Uppy plugin, backend routes, deployment diagram, persistence needs, tests, and operational responsibilities depend on this decision.

### ADR-005 — Storage backend and staging

- **Status:** Accepted 2026-10-23; concrete provider is deployment-specific.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Use private shared object storage for staging and final upload data, durable database-backed metadata for upload sessions, and stateless application workers that can access the same stores. Start with one supported storage profile; do not promise multiple providers.
- **Reason:** The required resume behavior spans process restarts and workers, so worker-local storage and process memory cannot be authoritative. Shared durable storage supports that topology without tying the architecture to a specific cloud vendor.
- **Consequences:** Object keys are server-generated and private. Final objects use immutable keys. Finalization verifies the object, then atomically commits the completed reference/state in the metadata store; object-store rename is not assumed atomic. Cleanup must be idempotent and scoped, with reconciliation for orphaned objects. The selected transport must integrate with this profile.
- **Boundary:** This decision does not select direct-to-object-storage transfer, a cloud provider, or a database engine; those depend on the transport and deployment profile. Numeric limits and retention values remain governed by the requirements and policy decisions.

### ADR-006 — Durable session state

- **Status:** Accepted 2026-10-23; database engine is deployment-specific.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Store authoritative session metadata in a durable database-backed store shared by application workers. Persist ownership, lifecycle state, expiry, transfer/integrity metadata, and staging/final object keys. Process memory may be used only as a cache, never as authoritative production state.
- **Reason:** Resume across process restarts and worker changes requires state to outlive and be visible beyond one worker.
- **Consequences:** State transitions and idempotency must use concurrency-safe updates. Schema evolution, failure recovery, and multi-worker behavior require tests. The service/database integration must not trust browser props to establish ownership, expiry, or completion.

### ADR-007 — Dash completion contract

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Expose `id`, `disabled`, `maxFileSize`, `maxFiles`, and `acceptedFileTypes` as component inputs; restrictions are browser feedback only. `uploadEvents` reports per-file `accepted`, `uploading`, and terminal `completed`/`failed`/`cancelled` transitions. `completedFiles` is cumulative and contains only server-confirmed opaque references plus safe metadata. Progress stays in the UI. Batches allow partial success and end when every file is terminal.
- **Reason:** Separating command/session acceptance from server-confirmed completion prevents callbacks from treating client claims as authoritative. Per-file outcomes support partial success without hiding successful files.
- **Consequences:** Acceptance means the server authorized and created the session. Events include stable correlation IDs; per-file order is guaranteed but cross-file order is not. Errors use stable public codes with safe messages and a retryable flag. References do not grant access by possession and never expose filesystem paths.

### ADR-008 — UI toolkit

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Use Uppy Dashboard for the first-release UI. Keep transport behind an adapter so the component choice does not decide the upload protocol.
- **Reason:** Uppy provides an established file-selection and progress experience while allowing the transport to be selected independently.
- **Consequences:** Validate keyboard operation, focus handling, labels, announcements, contrast, supported browsers, and bundle size. Client restrictions remain advisory; server policy is authoritative.

### ADR-009 — Supported runtime matrix

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Support Python 3.11–3.14; Dash `>=3.0,<5.0`; Node.js 22 and 24 for component builds; and the latest two stable releases of Chrome, Edge, Firefox, and Safari. Internet Explorer is not supported.
- **Reason:** This matrix provides a defined support boundary while avoiding an unnecessarily broad legacy compatibility promise.
- **Consequences:** CI must cover all supported Python versions, the minimum Dash version and each supported Dash major version, both build Node.js versions, and the browser support matrix before release. Revisit the matrix as runtimes reach end of support or new major versions are adopted.

### ADR-010 — Build artifacts and locks

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Use `uv` with `pyproject.toml`/`uv.lock` and Hatchling for Python; Node.js 22/24 with pnpm 10/`pnpm-lock.yaml` for TypeScript/React builds. Use Ruff, mypy, pytest, ESLint, Prettier, Vitest, and Playwright. TypeScript/React is authoritative; commit generated Dash Python bindings and JS/CSS bundles.
- **Reason:** One locked manager per ecosystem and a checked-in, reproducible component build make clean installs and package releases auditable.
- **Consequences:** CI regenerates artifacts and fails on drift, tests supported runtime matrices, builds wheel/sdist, and smoke-tests clean installs. End users do not need Node.js to install or run published artifacts. Tool versions must be pinned in project metadata and CI.

### ADR-011 — Browser origin and CSRF policy

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Browser upload access is same-origin, with CORS disabled by default. Cookie-authenticated requests must use the host application's CSRF protection.
- **Reason:** The package relies on host-app identity and must not make ambient browser credentials a cross-origin upload capability.
- **Consequences:** Cross-origin deployments require explicit security review and a documented exception. Browser integration tests must cover allowed and rejected origins and CSRF states.

### ADR-012 — Untrusted content handling

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** The upload service does not automatically unpack, render, or process uploaded content. Provide a host integration hook for scanning/quarantine where required; do not claim built-in malware scanning.
- **Reason:** Content is untrusted and safe processing depends on each host application's downstream systems and policy.
- **Consequences:** Treat MIME type and extension as untrusted metadata. Document downstream handling responsibilities and test the configured reject/hold path when a host scanning policy is enabled.

### ADR-013 — Resource limits and retention baseline

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Enforce 5 GiB per file; 64 MiB per request or chunk; 10 files and 10 GiB aggregate per batch; 3 concurrent transfers per user; and 10 GiB active staging data per user. Expire incomplete sessions after 24 hours idle and no later than 7 days after creation. The host application enforces completed-object quotas and owns successful-object retention/deletion. Keep completion metadata while its reference is valid and reconcile it when the object is deleted. Audit-log retention is host-controlled.
- **Reason:** Finite server-side limits and bounded staging retention reduce resource-exhaustion risk while allowing resumable large-file transfers. Completed data lifecycle belongs to the host application that owns the data.
- **Consequences:** Enforce each threshold at the HTTP/storage boundary and test just-over-limit behavior. These are initial product limits, not a throughput guarantee; benchmark the supported topology and update the ADR if measurements or user needs require a change. Proxy limits must accommodate the 64 MiB request/chunk cap.

### ADR-014 — Package identity and compatibility

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** Use `dash-file-uploader` as the intended package name under `rakrsh`. Verify registry name availability and publisher ownership before the first publication. Use a clean first-release API without a broad compatibility promise for either predecessor; provide migration guidance for documented behavior.
- **Reason:** The new project has a security and maintenance contract that should not inherit undocumented legacy behavior by default.
- **Consequences:** The package name remains subject to registry availability. Any compatibility adapter requires explicit review and must not weaken the security contract.

### ADR-015 — Sole-maintainer governance baseline

- **Status:** Accepted 2026-10-23.
- **Owner:** Project owner (`rakrsh`).
- **Decision:** `@rakrsh` is the sole maintainer, code owner, and release owner; no backup maintainer is currently appointed. Require pull requests to `main`, but do not require an approving review until another maintainer is available. Require CI before merge once issue #7 establishes the workflows. Use GitHub private vulnerability reporting, the Contributor Covenant 2.1, and the support lifecycle published in `SUPPORT.md`.
- **Reason:** The repository needs accountable ownership and safe contribution/reporting paths now, without making all changes unmergeable while there is only one maintainer.
- **Consequences:** The absence of a backup is a continuity risk. The no-approval exception is temporary and must be revisited when a second maintainer is appointed. Branch protection cannot require CI until the CI check names exist; issue #7 remains a dependency for that control.

## 3. Risk register

| ID | Risk | Likelihood / impact | Mitigation / owner action |
|---|---|---|---|
| **R-01** | Transport and deployment-specific provider choices remain undecided and cause architectural rework. | High / High | ADR-005/006 select the storage profile; resolve ADR-004 and confirm provider/database integration against the approved deployment before protocol implementation. |
| **R-02** | “No issues” is interpreted as a guarantee that cannot be made. | High / High | Define measurable security/reliability controls and release gates; communicate residual risk and scope. |
| **R-03** | Host application auth integration details are underspecified, leading to an open upload route. | Medium / Critical | Require authenticated host integration; define the API contract and test every lifecycle operation. |
| **R-04** | The approved limits may not match a deployment's capacity or user needs. | Medium / High | Enforce limits server-side, align proxy/storage configuration, benchmark the supported topology, and revise only through an approved decision. |
| **R-05** | A custom resumable protocol introduces race/corruption bugs. | Medium / High | Prefer a mature protocol where suitable; if custom, write protocol spec and adversarial/concurrency tests first. |
| **R-06** | Multi-worker deployment loses session state or cannot access staging data. | Medium / High | Choose durable shared state/storage or limit support explicitly; test the declared topology. |
| **R-07** | Legacy compatibility pressures weaken the new security contract. | Medium / High | Keep compatibility adapter optional and fail closed; provide a migration guide instead of insecure implicit behavior. |
| **R-08** | New project lacks a backup maintainer for ongoing dependencies and security response. | Medium / High | `@rakrsh` is the sole maintainer; private reporting and support policies are documented. Appoint a backup before stable production launch and revisit the PR approval rule. |
| **R-09** | Generated artifacts or dependencies make releases non-reproducible. | Medium / Medium | Lock dependencies; clean-build/package tests in CI; verify artifact contents. |
| **R-10** | Test suite covers only happy-path UI flows. | Medium / High | Make protocol, security, failure, concurrency, and packaging tests required gates. |
| **R-11** | Performance claims do not match production topology. | Medium / Medium | Publish reproducible benchmark parameters and measured envelope; avoid unqualified “unlimited” claims. |

## 4. Open questions for the project owner

These should be answered before finalizing the implementation plan:

1. Which concrete object-storage provider and database engine should the first deployment use, and does the selected transport require a separately deployed upload service? ADR-005/006 select shared object storage, durable session metadata, and stateless workers; ADR-004 remains open.
2. Are additional storage profiles required beyond the first-release private shared object-storage profile? Multiple providers are out of scope unless explicitly approved.
3. What identity/authorization API can the host app provide?
4. Which deployments require the host scanning/quarantine hook, and what backup policy applies?
5. Who can serve as backup maintainer? Currently none is appointed; resolve before stable production launch.

## 5. Decision review cadence

Revisit this register:

- before implementation of the upload protocol;
- before adding a storage backend or authentication mode;
- when changing the supported runtime matrix;
- before beta and stable release;
- after any incident, threat-model finding, or major upstream dependency change.

Record accepted decisions with date, owner, rationale, alternatives considered, and consequences. Superseded decisions should remain linked rather than silently erased.
