# Development Path and Milestones

## Guiding approach

Build vertical slices around verifiable behavior, not a large frontend-first rewrite. The sequence is: decide the protocol and support boundaries, prove secure server behavior, then integrate the Dash API and UI, then harden packaging and operations.

Every milestone must end with a runnable artifact, tests, updated documentation, and a reviewable decision record. Do not mark work complete based on implementation alone.

## Phase 0 — Product, ownership, and constraints

**Work**

- Confirm maintainers, repository/package name, license, and package registry ownership.
- Decide whether a new public package is a successor or an independent tool.
- Gather file-size, concurrency, storage, deployment, resumability, and retention requirements.
- Select supported Python/Dash/browser/Node versions based on intended users.
- Choose the initial deployment profile and authentication integration boundary.
- Review and approve [requirements](./03-requirements.md) and [threat model](./04-security-threat-model.md).

**Deliverables**

- Product scope and support matrix.
- Requirement values for currently TBD limits.
- Initial ADRs for transport, storage, state persistence, and compatibility.

**Exit gate:** no unresolved decision that changes the protocol or security model.

## Phase 1 — Repository and development foundations

**Work**

- Create the new repository with branch protection, issue/PR templates, CODEOWNERS, contribution guide, and security reporting process.
- Establish Python and JavaScript/TypeScript package layout.
- Configure lockfiles and reproducible toolchain installation.
- Add formatting, lint, typing, test, build, and package-inspection commands.
- Build a minimal generated Dash component from a clean checkout.
- Add a CI smoke test that builds and imports the package.

**Deliverables**

- Reproducible development environment.
- CI pipeline for lint, type checks, tests, build, and install smoke test.
- Architecture and decision docs in the repository.

**Exit gate:** a contributor can clone the repo, install locked dependencies, build, test, and import without undocumented local artifacts.

## Phase 2 — Backend session and policy vertical slice

**Work**

- Implement app-scoped configuration and route registration.
- Implement upload-session creation, state storage, expiry, and authorization integration.
- Implement server-generated session/storage keys.
- Define and implement request validation and public error responses.
- Enforce the first complete set of server-side size/count/time limits.
- Add HTTP-level tests before connecting the frontend.

**Deliverables**

- Session API with documented state transitions.
- Policy interfaces and denial behavior.
- Tests for invalid requests, unauthenticated requests, quota failures, and two-app isolation.

**Exit gate:** a test client can create/deny a session predictably, and hostile client input cannot create an unsafe path or bypass policy.

## Phase 3 — Transfer and safe finalization

**Work**

- Implement the chosen transport (single request, resumable protocol, or direct storage) according to its ADR.
- Implement bounded data transfer into server-generated staging storage.
- Add duplicate/retry/concurrency behavior and integrity checks as required.
- Implement finalization, atomic publication, cancellation, and cleanup.
- Add fault injection for process/storage errors.

**Deliverables**

- Transfer API and storage implementation.
- State transition tests, concurrency tests, interruption tests, and cleanup tests.
- Resource usage baseline for the agreed maximum file size.

**Exit gate:** incomplete or unauthorized uploads never appear as complete; retries and concurrent operations meet the documented protocol.

## Phase 4 — Dash component and callback contract

**Work**

- Build the minimal UI for selection, transfer, progress, success/failure, retry, and cancellation.
- Connect UI actions to the protocol and expose server-confirmed completion references.
- Implement app callback integration with stable types and documented trigger semantics.
- Test disabled, repeat upload, multi-file, network failure, and callback ordering.
- Verify accessibility and base-path/proxy deployment.

**Deliverables**

- Public Python API and component props.
- Dash callback examples and API documentation.
- Browser integration suite for supported browsers.

**Exit gate:** browser and callback results agree with server-side session state in success and failure scenarios.

## Phase 5 — Operational hardening and performance

**Work**

- Test the selected worker topology, reverse proxy, storage, and restart behavior.
- Test the maximum configured file size and concurrency; tune timeouts and quotas.
- Verify cleanup under normal operation and simulated process crashes.
- Add structured metrics/logging and operator health checks.
- Review privacy, retention, and access logs.

**Deliverables**

- Deployment guide and supported topology statement.
- Reproducible benchmark/load-test report with environment parameters.
- Operations runbook for quota/storage/cleanup failures.

**Exit gate:** the team accepts the measured operating envelope and limitations.

## Phase 6 — Beta, migration, and first stable release

**Work**

- Publish a beta for representative Dash applications.
- Collect feedback on API ergonomics, deployment friction, and migration requirements.
- Fix release-blocking defects; do not weaken security controls for superficial compatibility.
- Complete package metadata, changelog, license, migration guide, and release notes.
- Run final security and release checklists.

**Deliverables**

- Beta feedback summary and resolved issues.
- Versioned release candidate and clean-install verification.
- Stable release with support policy and security contact.

**Exit gate:** all release gates in [the SDLC and release plan](./06-sdlc-quality-and-release.md) pass.

## Workstream dependencies

```text
Requirements / threat model
           |
           v
Transport + storage + state ADRs
           |
           v
Backend session/policy -> transfer/finalize -> Dash API/UI
           |                                  |
           +----------- integration tests ----+
                              |
                              v
                operations / beta / release
```

Some work can run in parallel after the relevant contract is stable: docs scaffolding, CI setup, component visual design, and test harnesses. Do not implement transport and UI independently before the protocol is agreed.

## Definition of ready

A work item is ready when:

- its user-visible or operational outcome is stated;
- acceptance criteria are testable;
- related requirements and threat scenarios are linked;
- API, compatibility, and failure behavior are identified;
- dependencies and migration impact are understood;
- it has an owner and review plan.

## Definition of done

A work item is done only when:

- implementation and focused tests are complete;
- security/privacy implications have been checked;
- format, lint, type, and relevant test checks pass;
- docs and examples are updated;
- generated artifacts/build outputs are reproducible;
- failure paths and observability are covered;
- changes are reviewed and linked to their requirement/ADR.
