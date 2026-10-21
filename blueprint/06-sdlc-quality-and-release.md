# SDLC, Quality, and Release Process

## 1. Repository governance

Before public development:

- identify maintainers and code owners;
- protect the default branch and require reviewed pull requests;
- provide issue, bug, feature, and security-reporting templates;
- publish a contribution guide and code of conduct appropriate to the project;
- define supported versions and end-of-support policy;
- define who can publish packages and how credentials are protected;
- document how security issues are handled privately before public disclosure.

Use issues or equivalent work tracking with links to requirements, threat scenarios, or ADRs. Changes to protocol, authorization, storage, dependencies, generated artifacts, or callback semantics require explicit review ownership.

## 2. Branch and pull-request workflow

Recommended default:

- short-lived feature branches;
- protected `main`;
- small PRs with a clear objective and test evidence;
- required CI checks and at least one qualified reviewer;
- additional security review for authentication, authorization, path/storage handling, transport, and dependency changes;
- release tags created only from reviewed commits.

PR description checklist:

1. Requirement or defect addressed.
2. User-visible/API/operational behavior change.
3. Security and privacy impact.
4. Tests added/updated and exact commands/results.
5. Docs/migration impact.
6. Generated files/lockfile changes and how they were produced.

## 3. Development environment and source of truth

Choose and document one toolchain for each ecosystem:

- Python packaging/build backend and lock strategy.
- Node.js version and one package manager/lockfile.
- TypeScript/React and generated Dash component workflow.

Do not maintain multiple competing lockfiles unless CI verifies they represent the same dependency resolution. Decide whether generated Dash bindings and bundles are committed or generated during packaging; test that policy from a clean clone.

Provide one documented command per major task, for example:

- install development dependencies;
- format/lint/type-check;
- run backend unit tests;
- run protocol/integration tests;
- run frontend tests;
- build generated component/package;
- build wheel and source distribution;
- verify install from built artifacts.

## 4. Test strategy

### Python unit tests

Cover configuration validation, app isolation, limits, state transitions, key generation, error mapping, expiry, and cleanup logic. Avoid browser dependencies for tests that can run at the API/model level.

### HTTP/protocol integration tests

Exercise the real Flask/Dash endpoint using a test client and the chosen storage/session implementation. Include malformed multipart, authorization, path attacks, quotas, retries, duplicate requests, cancellation, finalization, and error response contracts.

### Frontend tests

Test user actions, prop updates, event ordering, asynchronous errors, repeated batches, cancellation/retry, and component cleanup. Mock the server only for UI-specific behavior; keep separate tests against the real protocol.

### Browser end-to-end tests

Run representative upload scenarios in supported browsers, including reverse-proxy/base-path mode if supported. Validate not only displayed success but also server-side stored data, session state, callback data, and cleanup.

### Concurrency, resilience, and load tests

Use the deployment topology from the support matrix. Test duplicate and concurrent requests, worker restart, storage failures, incomplete sessions, selected maximum size, and agreed concurrent-upload levels. Record exact hardware, network, proxy, worker, and storage conditions with every performance claim.

### Packaging tests

Build wheel and source distribution from a clean tag/check-out; install each in a clean environment; import and run a minimal Dash app; verify package data includes the component bundle and metadata.

## 5. CI gates

Every PR should run:

1. formatting and lint;
2. Python type/static checks selected by the project;
3. Python unit and HTTP integration tests;
4. TypeScript type-check and frontend tests;
5. component/package build;
6. wheel/sdist build and package-content verification;
7. clean install/import smoke test;
8. dependency and secret scanning;
9. focused security tests for changes to the upload boundary.

Release CI additionally runs the declared Python/Dash compatibility matrix and supported browser E2E tests. Optional/slow jobs may be separate, but release gates must be explicit rather than silently skipped.

## 6. Compatibility policy

Before the first public release, publish:

- supported Python versions;
- supported Dash versions;
- supported browsers and browser feature assumptions;
- Node/package-manager versions needed to build from source;
- deployment profiles and worker/process constraints;
- storage backends and consistency guarantees;
- API stability and deprecation policy.

Only claim a version as supported if CI or a clearly described validation process covers it. Upgrade dependencies deliberately and run compatibility tests before changing lower/upper bounds.

## 7. Versioning and releases

Use semantic versioning only after defining what constitutes a public API: Python function signatures, component props, callback payloads, error codes, and storage/session behavior.

Release steps:

1. Confirm all issue and release gates are satisfied.
2. Update version, changelog, migration notes, and support matrix.
3. Build artifacts in a clean CI environment.
4. Inspect wheel/sdist contents and metadata.
5. Install artifacts in a clean environment and run smoke tests.
6. Publish using protected credentials/provenance controls available to the chosen registry.
7. Create an immutable source tag and release notes.
8. Verify registry install and package import after publication.
9. Maintain rollback/yank guidance if a broken artifact is published.

Do not publish a release candidate as stable while security tests, supported-runtime CI, or package installation is failing.

## 8. Documentation requirements

The repository should maintain:

- README quick start and honest scope statement;
- API reference for Python functions and component props;
- architecture and protocol documentation;
- deployment guide for every supported topology;
- security and privacy responsibilities;
- limits, retention, cleanup, and storage behavior;
- troubleshooting and stable error codes;
- migration guide from both reference packages if compatibility is intended;
- changelog, contribution guide, support policy, and security contact.

## 9. Operations and incident response

Document how operators:

- configure request/body limits and timeouts in proxies;
- configure authentication/authorization and CSRF behavior;
- provision storage permissions, quotas, monitoring, backups, and retention;
- inspect upload failures and cleanup backlog;
- rotate secrets and storage credentials;
- report security issues;
- respond to storage exhaustion, suspected unauthorized upload, or corrupted finalization.

Operational logs should use correlation IDs and structured event types; avoid content, secrets, and unnecessary personal data.

## 10. Release checklist

- [ ] Requirements and accepted exceptions reviewed.
- [ ] Threat model updated for architecture/dependency changes.
- [ ] Server-side authorization, path containment, limits, and error-contract tests pass.
- [ ] Retry/concurrency/finalization/cleanup tests pass.
- [ ] Supported runtime and browser matrices pass.
- [ ] Clean build, wheel/sdist install, and import checks pass.
- [ ] Dependency/license/package contents reviewed.
- [ ] Docs, migration guide, changelog, and support policy updated.
- [ ] Security contact and release ownership are active.
- [ ] Release artifacts and source tag point to the reviewed commit.
