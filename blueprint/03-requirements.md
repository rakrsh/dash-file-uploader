# Product and Technical Requirements

## 1. Purpose

Define an implementable first-release contract for a maintained Dash upload component. Requirements are written so they can be traced to architecture, tests, and release gates.

### Requirement status

- **MUST**: release-blocking requirement.
- **SHOULD**: expected unless the project owner records an approved exception.
- **TBD**: needs an owner decision before implementation; it is not a default or an implied promise.

## 2. Users and actors

- **Application developer:** installs the package, configures the app, and consumes callback results.
- **End user:** selects, uploads, retries, or cancels files through the browser.
- **Host application:** authenticates users and provides authorization policy.
- **Operator:** configures storage, limits, reverse proxy, retention, monitoring, and deployment.
- **Maintainer:** reviews changes, triages defects, releases supported versions, and handles security reports.

The first release targets internal and customer-facing Dash applications whose users are authenticated by the host application. Anonymous/public uploads are excluded.

## 3. Product scope

### In scope

- Dash component for selection, progress, and upload interaction.
- Python configuration bound to an individual Dash app.
- Server endpoint(s) for upload-session creation, transfer, completion, and cancellation as selected by the protocol ADR.
- Server-side enforcement of configured limits and access policy.
- Safe metadata and stable upload references for Dash callbacks.
- Cleanup and operational observability for incomplete uploads.

### Out of scope for the first release unless explicitly approved

- Content transformation or media processing.
- Built-in user identity provider.
- Malware scanning service (integration hook may be required by the threat model).
- Multiple storage providers.
- Anonymous/public upload mode.
- Broad compatibility with either predecessor package or its undocumented legacy behavior. The first release uses a clean API and provides migration guidance.

## 4. Functional requirements

### Configuration and component

- **FR-001 MUST:** Each Dash app has independent uploader configuration; configuration in one app cannot alter another app.
- **FR-002 MUST:** The Python API validates component configuration and rejects unknown or invalid options clearly.
- **FR-003 MUST:** The component supports a documented list of restrictions and clearly distinguishes browser feedback from server-enforced policy.
- **FR-004 SHOULD:** The component communicates progress, retryable failure, terminal failure, cancellation, and completion accessibly.
- **FR-005 MUST:** A component action result distinguishes command acceptance from asynchronous upload completion.
- **FR-006 MUST:** A callback receives only a server-confirmed completion reference and documented safe metadata; it must not trust client-reported completion as authoritative.

### First-release component contract

Inputs:

- `id`: required Dash component identifier.
- `disabled`: disables file selection and upload actions.
- `maxFileSize`: positive maximum size in bytes for browser feedback.
- `maxFiles`: positive file-count restriction for browser feedback.
- `acceptedFileTypes`: list of extensions or MIME types using the browser `accept` convention.

The three file restrictions are user-experience hints only. The server independently enforces the approved application policy. Authentication, storage credentials, server paths, and authorization decisions are never component props.

Outputs:

- `uploadEvents`: emits a per-file transition with `eventId`, `batchId`, `fileId`, and `status` (`accepted`, `uploading`, `completed`, `failed`, or `cancelled`). `accepted` means the server accepted and authorized the session, not merely that the browser received a command. A failed event includes a stable error `code`, safe `message`, and `retryable` flag.
- `completedFiles`: cumulative per-file records containing only a server-confirmed opaque `uploadRef`, `batchId`, `filename`, `size`, and `mediaType`. A reference is not a bearer credential and grants no access by itself.

Progress is rendered by the component and does not trigger a Dash callback for every progress update. Files in a batch have independent outcomes; successful files remain available when another file fails. A batch is terminal when every file is completed, failed, or cancelled. Per-file events preserve transition order, but no ordering is promised between different files. Errors never expose paths, stack traces, secrets, or storage details.

The initial public error-code catalog is `INVALID_REQUEST`, `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `LIMIT_EXCEEDED`, `INVALID_STATE`, `UPLOAD_EXPIRED`, `UPLOAD_CANCELLED`, `INTEGRITY_FAILED`, `STORAGE_UNAVAILABLE`, `TRANSFER_FAILED`, and `INTERNAL_ERROR`. Codes and meanings are stable public API; messages may be clarified without changing codes.

### Upload session and transfer

- **FR-007 MUST:** Every upload has a server-tracked lifecycle and owner/authorization context.
- **FR-008 MUST:** The server validates every create, transfer, finalize, cancel, status, and retry operation against the session state and policy.
- **FR-009 MUST:** Upload data is written to server-generated staging keys; original names are metadata and are never path components.
- **FR-010 MUST:** The server enforces these first-release limits: 5 GiB per file; 64 MiB per request or chunk; 10 files and 10 GiB aggregate per batch; 3 concurrent transfers per user; and 10 GiB of active staging data per user. The host application enforces quotas for completed objects.
- **FR-011 MUST:** Duplicate and retry behavior is defined and idempotent where the client may retry.
- **FR-012 MUST:** A file is reported as completed only after server-side completeness and policy checks and successful publication.
- **FR-013 MUST:** Finalization does not expose partial data and has defined atomicity semantics for the chosen storage backend.
- **FR-014 SHOULD:** The user can cancel an upload; cancellation prevents further transfer/finalization and schedules safe cleanup.
- **FR-015 MUST:** Uploads resume after network interruption, browser reload, application/process restart, and requests reaching a different worker. The selected transport and durable shared state/storage must implement and verify these guarantees.

### Authorization and integration

- **FR-016 MUST:** The package provides a documented hook/integration for the host application to authorize upload creation and subsequent operations.
- **FR-017 MUST:** Possession of a client-provided upload ID or file reference alone does not authorize access.
- **FR-018 MUST:** The package supports proxy/base-path deployment as specified in the compatibility matrix.
- **FR-019 MUST:** The package returns stable, documented error codes without exposing server internals.

### Cleanup and audit

- **FR-020 MUST:** Incomplete sessions expire after 24 hours without activity and no later than 7 days after creation. Cleanup is retryable. Completed objects are retained or deleted by the host application, not automatically by the uploader.
- **FR-021 MUST:** Cleanup is scoped to the session’s staging data, safe to retry, and observable.
- **FR-022 SHOULD:** The system emits auditable lifecycle events without recording file content, secrets, or unnecessary personal data.

## 5. Non-functional requirements

| ID | Requirement |
|---|---|
| **NFR-001 Security** | Threat-model controls in [`04-security-threat-model.md`](./04-security-threat-model.md) are release gates; security is not inferred from successful UI tests. |
| **NFR-002 Memory** | The server must not buffer an entire configured maximum-size file in application memory. Verify with a bounded-memory integration test. |
| **NFR-003 Scalability** | Supported worker/process topology and shared-state/storage requirements are documented and tested. |
| **NFR-004 Reliability** | Retry, duplicate transfer, cancellation, interruption, and finalization semantics are deterministic and covered by tests. |
| **NFR-005 Performance** | Define target file sizes, concurrency, network, storage, and latency before benchmarking. No performance claim is permitted without reproducible benchmark parameters. |
| **NFR-006 Accessibility** | Keyboard operation, focus handling, labels, status announcements, and contrast are checked for the supported UI. |
| **NFR-007 Compatibility** | Support Python 3.11–3.14; Dash `>=3.0,<5.0`; Node.js 22 and 24 for component builds; and the latest two stable releases of Chrome, Edge, Firefox, and Safari. No Internet Explorer support. CI exercises declared runtimes or clearly marks best-effort coverage. |
| **NFR-008 Observability** | Operators can distinguish validation, authorization, transport, storage, finalization, and cleanup failures using structured logs/metrics. |
| **NFR-009 Privacy** | Retention, metadata collection, logging, and file deletion behavior are documented and configurable where required. |
| **NFR-010 Maintainability** | Clean-checkout builds are reproducible; generated artifacts and lockfiles have documented source-of-truth rules. |

## 6. User stories and acceptance examples

1. As an application developer, I can configure two Dash apps independently, and each uses its own route, policy, and storage configuration.
2. As an end user, I can see whether an upload was accepted, is progressing, completed, or failed without confusing command receipt with transfer completion.
3. As an operator, I can set upload limits and verify that requests exceeding them are rejected by the server even when sent without the component UI.
4. As a user, I cannot access another user’s upload by changing an upload ID or file reference.
5. As an application, I receive a completed file reference only after the server has verified and published the file.
6. As an operator, abandoned staging data is removed according to retention policy and cleanup failures are visible.

## 7. Measurable acceptance criteria

- Invalid path-like filenames and identifiers never change the resolved storage root or target an unintended location.
- A configured maximum is enforced via direct endpoint requests as well as through the browser.
- No unauthorized session can be read, written, finalized, cancelled, or deleted by another principal.
- A file interrupted before finalize never appears as completed in Dash callback data.
- Retrying the same permitted operation produces the documented result without duplicate publication or corruption.
- Two app instances configured differently in one process pass isolation tests.
- For the selected maximum file size, a load test demonstrates the agreed memory, storage, and throughput bounds. Numeric thresholds remain **TBD** until deployment assumptions are supplied.
- The built wheel and source distribution install and pass import/smoke tests from clean environments.

## 8. Decisions required before implementation

The following decisions remain open:

- concrete object-storage provider and database engine;
- upload transport/protocol implementation for the accepted resume requirement;
- host authentication/authorization API integration details;
- whether host-provided scanning/quarantine is mandatory for each deployment and the applicable backup policy;
- concrete reverse-proxy configuration for the selected deployment.

The intended package name is `dash-file-uploader` under `rakrsh`; verify name availability in the package registry before first publication. No broad compatibility with predecessor packages is promised; provide migration guidance for documented behavior.

Track decisions in [`07-decisions-risks-and-open-questions.md`](./07-decisions-risks-and-open-questions.md).
