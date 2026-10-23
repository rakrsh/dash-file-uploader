# SDLC, Quality, and Release Process

## 1. Repository governance

Repository governance is recorded in the root `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `SUPPORT.md`, plus `.github/` issue forms, pull-request template, and `CODEOWNERS`.

- **Maintainer and code owner:** `@rakrsh` is the sole maintainer and release owner. `@rakrsh` owns all files in `CODEOWNERS`. No backup maintainer is currently appointed.
- **Publishing:** only `@rakrsh` may publish the intended `rakrsh` distribution. Require multi-factor authentication on the publishing account and prefer registry-supported trusted publishing/OIDC over long-lived credentials. Verify ownership and name availability before the first release.
- **Security reporting:** use GitHub private vulnerability reporting; keep vulnerability handling private until a coordinated disclosure. Verify the GitHub feature is enabled in repository settings before the first public release. The response targets in `SECURITY.md` are goals, not an SLA.
- **Support lifecycle:** use the release lifecycle in `SUPPORT.md` and the runtime matrix in section 6.
- **Templates and contributions:** use the checked-in issue forms, PR template, contribution guide, and code of conduct.

Repository settings and checked-in policies must agree. The current single-maintainer exception to independent PR approval is recorded in ADR-015 and must be revisited when a backup maintainer is appointed.

Use issues or equivalent work tracking with links to requirements, threat scenarios, or ADRs. Changes to protocol, authorization, storage, dependencies, generated artifacts, or callback semantics require explicit review ownership.

## 2. Branch and pull-request workflow

Current policy:

- use short-lived feature branches and submit all changes to `main` by pull request; direct pushes are disallowed;
- require CI checks before merge as soon as the workflows from issue #7 are available;
- while `@rakrsh` is the sole maintainer, do not require an independent approving review, which would make normal changes unmergeable; obtain maintainer review where practicable and revisit this exception when a second maintainer is added;
- require additional security review for authentication, authorization, path/storage handling, transport, and dependency changes;
- create release tags only from reviewed commits.

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

### Approved toolchain baseline

- **Python:** `uv` with `pyproject.toml` and one committed `uv.lock`; Hatchling builds the package. Use Ruff for linting/formatting, mypy for static typing, and pytest for tests.
- **Frontend:** Node.js 22 and 24 for builds; pnpm 10 with one committed `pnpm-lock.yaml`; TypeScript/React source with ESLint, Prettier, and Vitest.
- **Browser testing:** Playwright for end-to-end tests in the supported browser matrix.
- **Generated artifacts:** TypeScript/React is the source of truth. Commit generated Dash Python bindings and JS/CSS bundles; CI rebuilds them and fails if generated files drift. Published artifacts include the bundle so consumers do not need Node.js at runtime.

The repository bootstrap should expose one documented command per task, implemented as package scripts or `uv run` commands. Initial command names are `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run pytest`, `pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, and `uv build`. CI must exercise Python 3.11–3.14 and Node.js 22/24, verify generated artifacts are reproducible, build wheel and sdist, and install/smoke-test both in clean environments. These commands become executable as the project scaffold is established.

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

The approved first-release support matrix is Python 3.11–3.14; Dash `>=3.0,<5.0`; Node.js 22 and 24 for component builds; and the latest two stable releases of Chrome, Edge, Firefox, and Safari. Internet Explorer is not supported. CI must exercise each supported Python version, the minimum Dash version and supported Dash major versions, both build Node.js versions, and the supported browser matrix before release.

The intended distribution name is `dash-file-uploader` under the `rakrsh` publisher. Verify name availability and publisher ownership in the chosen package registry before the first publication.

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

The root governance files and GitHub templates are the source of truth for contributor conduct, vulnerability reporting, issue intake, and support lifecycle.

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
