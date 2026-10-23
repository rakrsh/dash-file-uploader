# Security and Privacy Threat Model

## 1. Status and scope

This is an initial threat model for the proposed new Dash upload project. It is not a penetration test, certification, or guarantee of zero vulnerabilities. It must be reviewed against the final protocol, deployment topology, and storage provider before implementation and before each major release.

Reference findings from both existing repositories are summarized in [`01-architecture-extraction.md`](./01-architecture-extraction.md).

### Approved first-release policy baseline

- Uploads require an authenticated host application; anonymous/public upload is excluded.
- The host authorization policy is checked for every upload lifecycle operation and completion-reference access.
- Browser access is same-origin with no CORS enabled by default. Cookie-authenticated requests require the host application's CSRF protection.
- The upload service does not automatically unpack, render, or process uploaded content. A host scanning/quarantine integration hook is available; malware scanning is not built in.
- Enforced limits are 5 GiB per file, 64 MiB per request/chunk, 10 files and 10 GiB per batch, 3 concurrent transfers per user, and 10 GiB of active staging data per user. Completed-object quotas are host-policy-enforced.
- Incomplete staging expires after 24 hours idle, with a 7-day maximum session age. The host application owns completed-object retention and deletion.

## 2. Assets

- Uploaded file contents and derived previews.
- User/application identity and authorization decisions.
- Upload session records and opaque references.
- Staging and finalized objects/files.
- Storage capacity, CPU, memory, worker capacity, and network bandwidth.
- Application callbacks and downstream processing systems.
- Session secrets, signing keys, and object-storage credentials.
- Audit records and operational logs.

## 3. Trust boundaries

1. **Browser to Dash/upload API:** all request bodies, form fields, component props, filenames, MIME types, sizes, upload IDs, and completion claims are untrusted.
2. **Dash application to host authentication:** identity is trusted only after the host application's normal authentication has run and is bound to the request.
3. **Upload API to session store:** session state must be authorized, durable as required, and updated consistently.
4. **Upload API to staging/final storage:** storage keys and deletion scopes must be generated/verified server-side.
5. **Reverse proxy to application:** body limits, timeouts, path-prefix rewriting, and client address headers must be configured deliberately.
6. **Application callbacks to uploaded objects:** callback references are identifiers, not bearer authorization, unless explicitly designed and documented as such.

## 4. Threat scenarios and required controls

| ID | Threat | Required controls | Verification |
|---|---|---|---|
| **TH-01** | Path traversal or path confusion through filename, upload ID, or multipart metadata | Never use client strings as storage paths. Generate storage keys server-side. Resolve and assert containment for all file operations. Reject malformed values. | Unit/property tests for separators, `..`, absolute paths, Unicode, NUL/control characters, long strings, and platform-specific path forms. Assert no outside-root file is created, read, overwritten, or deleted. |
| **TH-02** | Cross-user upload access by guessing/replaying an upload ID or file reference | Bind session to verified principal/tenant. Authorize every operation. Use opaque identifiers, but do not rely on opacity alone. | Two-principal integration tests for read/write/finalize/cancel/status and replay. |
| **TH-03** | Unbounded uploads exhaust disk, temp storage, memory, workers, or bandwidth | Enforce the approved request/chunk, file, batch, per-user staging, concurrency, and expiry limits; use bounded streaming, admission control, proxy alignment, and disk monitoring. | Direct endpoint tests just over each configured bound; load/soak tests; cleanup tests. |
| **TH-04** | Forged completion props cause callbacks to process incomplete or unauthorized files | Server session state is authoritative. Callback resolves a server-verified completed reference. Do not trust browser filename/size/completion props. | Attempt callback updates with fabricated IDs and incomplete sessions. |
| **TH-05** | Race/replay/duplicate chunks corrupt or overwrite files | Explicit session state machine, idempotency keys, per-session concurrency control, safe staging, verified finalization, atomic publish. | Concurrent duplicate, reordered, retried, and interrupted transfer tests. |
| **TH-06** | Malicious or misleading content attacks downstream consumers | Treat content type/extension as untrusted. Do not automatically unpack, render, or process content. Provide a host scanning/quarantine hook where required; use safe download headers and downstream isolation. | Test spoofed MIME/extensions; verify configured scanning policy and reject/hold states where enabled. |
| **TH-07** | CSRF or ambient browser credentials cause unauthorized uploads | Same-origin only and no CORS by default. Cookie-authenticated requests use host-app CSRF protection; authorize every operation. | Browser integration tests with valid/invalid origin and CSRF state for the supported deployment. |
| **TH-08** | Internal paths, exception details, or secrets leak through errors/logs | Stable public error codes; protected internal diagnostics; redact credentials and sensitive metadata. | Error contract tests and log-redaction tests. |
| **TH-09** | Temporary files persist after cancellation, failed finalize, or process crash | Expire incomplete sessions after 24 hours idle and at 7 days maximum; use safe retryable cleanup and reconcile storage against durable session state. Completed-object deletion is host-owned. | Simulate crash at each lifecycle transition and verify eventual safe cleanup and host-owned deletion behavior. |
| **TH-10** | Malicious archive/image/document harms users or downstream processors | Do not automatically unpack/render/process untrusted data in the upload service. Use isolated downstream processing and explicit limits if such features are added. | Security review of any preview, extraction, conversion, or processing extension. |
| **TH-11** | Dependency compromise or vulnerable frontend/backend dependency | Lockfiles, reviewed dependency updates, provenance where available, automated scanning, minimal runtime dependencies. | CI dependency checks and documented update cadence; release review of changes. |
| **TH-12** | Multi-app or multi-tenant configuration leaks routes, folders, or policies | App-scoped configuration; no mutable module-level app settings; explicit tenant ownership. | Same-process app isolation and concurrent tenant integration tests. |

## 5. Minimum security requirements

- **SEC-001 MUST:** Every endpoint has an explicit authentication/authorization expectation; first-release upload access requires an authenticated host application and excludes anonymous uploads.
- **SEC-002 MUST:** Every operation is authorized against the server-side upload session and principal.
- **SEC-003 MUST:** Client-provided path-like data is never used as a path or deletion scope.
- **SEC-004 MUST:** All configured resource limits are enforced by server code and aligned with the proxy.
- **SEC-005 MUST:** Uploads remain in a private staging state until verified finalization.
- **SEC-006 MUST:** Finalization and cleanup are bounded to server-generated session-owned keys.
- **SEC-007 MUST:** Errors exposed to clients do not include stack traces, absolute paths, or secret values.
- **SEC-008 MUST:** Security-sensitive state and authorization decisions are tested at the HTTP integration layer.
- **SEC-009 SHOULD:** Logs include a correlation/session reference that does not expose a bearer secret.
- **SEC-010 MUST:** Security and privacy review is repeated when transport, storage, authentication, or callback semantics change.
- **SEC-011 MUST:** Cross-origin access is disabled by default; cookie-authenticated upload requests are covered by host-app CSRF protection and same-origin behavior is tested.

## 6. Secure lifecycle model

Suggested server-side states:

```text
CREATED -> RECEIVING -> FINALIZING -> COMPLETED
    |           |             |
    +----------> CANCELLED <---+
    +----------> EXPIRED
                RECEIVING -> FAILED
                FINALIZING -> FAILED
```

Transitions must be validated server-side. Terminal-state behavior, retry allowances, and cleanup scheduling need a written contract. A failed/cancelled/expired session must not be finalized merely because the browser reports success.

## 7. Data minimization and retention

- Store only metadata needed for authorization, integrity, callback results, audit, and cleanup.
- Decide whether original filenames are retained and who can view them.
- Avoid logging filename/content unless explicitly justified.
- Expire incomplete staging after 24 hours idle and no later than 7 days after session creation.
- The uploader does not automatically delete completed objects; the host application owns successful-file retention/deletion and completed-object quota enforcement.
- Keep completion metadata while its reference remains valid and reconcile metadata when the host deletes the object. Host operators control audit-log retention and backups.
- Avoid returning absolute server filesystem paths to the browser.

## 8. Security test plan

Before beta:

1. Test malformed multipart and missing-field requests.
2. Test filename and identifier path attacks across supported operating systems.
3. Test unauthorized cross-session and cross-tenant access.
4. Test every quota through direct HTTP calls.
5. Test CSRF/origin assumptions for the supported auth topology.
6. Test duplicate and concurrent finalization, retries, and cleanup.
7. Verify errors and logs do not disclose sensitive internals.
8. Run a threat-model review against the final deployment diagram.
9. Obtain an independent security review before public production claims if the project accepts untrusted/public uploads.

## 9. Deployment boundary

The package cannot make a deployment secure by itself. Operators must configure TLS, reverse-proxy request/body/time limits, authentication, storage permissions, secret management, disk monitoring, retention, backups, and any content scanning needed by their threat model. Document exactly which protections are library-provided and which are operator responsibilities.
