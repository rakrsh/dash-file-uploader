# Architecture Extraction and Comparison

## Purpose and method

This document records the architecture observed in the two reference projects and distinguishes observed facts from proposed design. The goal is not to copy either implementation. It is to identify useful patterns and explicitly prevent known shortcomings from becoming part of the replacement.

### Sources inspected

- Legacy repository: local checkout of [`fohrloop/dash-uploader`](https://github.com/fohrloop/dash-uploader), branch `dev`, commit `e1a1af4`; the README marks it archived on 2025-07-19.
- Uppy-based repository: [`Ozx-68102/dash-uploader-uppy5`](https://github.com/Ozx-68102/dash-uploader-uppy5), revision [`a71c145fa79b7459ffd83002ca301bbe670bde7e`](https://github.com/Ozx-68102/dash-uploader-uppy5/commit/a71c145fa79b7459ffd83002ca301bbe670bde7e), inspected 2026-10-21.

The Uppy source links below are pinned to that revision to make the observations reproducible. The legacy links point at the local workspace paths when useful.

## 1. Legacy `dash-uploader` architecture

### Components and responsibilities

| Component | Responsibility |
|---|---|
| Python `Upload` factory | Builds the generated Dash component props, generates an upload ID when omitted, and converts MB options into byte values. [`upload.py`](../dash_uploader/upload.py) |
| `configure_upload` | Stores configuration and registers GET and POST routes on the Dash/Flask server. [`configure_upload.py`](../dash_uploader/configure_upload.py) |
| React component | Uses Flow.js, performs browser-side restrictions, displays progress and controls, and updates Dash props. [`Upload_ReactComponent.react.js`](../src/lib/components/Upload_ReactComponent.react.js) |
| Flask request handler | Receives chunks, writes temporary chunk files, concatenates completed chunks, and removes temporary chunk directories. [`httprequesthandler.py`](../dash_uploader/httprequesthandler.py) |
| Callback wrapper | Converts component props to paths and `UploadStatus`, then invokes the decorated user callback. [`callbacks.py`](../dash_uploader/callbacks.py) |
| Generated build package | Contains generated Dash component Python bindings, metadata, and bundled JavaScript. It is required by package imports but absent from this checkout until the build runs. |

### Request and callback flow

1. The Dash app calls `configure_upload`.
2. The app layout creates an `Upload` component.
3. Flow.js sends chunked POST requests containing client-controlled upload and file metadata.
4. The Flask handler writes chunks under a directory derived from the configured folder and request fields.
5. The final chunk causes the handler to concatenate chunks into the final file.
6. The browser updates Dash props after each file succeeds.
7. The callback wrapper creates `UploadStatus` and invokes the application callback.

### Notable observed design properties

- Chunking is implemented by the project’s own filesystem handler.
- The React code sets `testChunks: false`, so Flow.js’s normal server-side chunk existence/resume check is disabled.
- The callback API relies on component props for filenames and upload IDs.
- Configuration is stored in module-level settings, including the app and upload root.
- The default handler uses request values in filesystem path construction without a demonstrated root-containment check.
- File size and extension restrictions are enforced by the client component, not by equivalent server-side policy.
- Broad exception handlers log tracebacks and return implicitly.
- The repository’s tests focus mainly on browser behavior and cover little of the HTTP/filesystem boundary.

## 2. `dash-uploader-uppy5` architecture

### Components and responsibilities

| Component | Responsibility |
|---|---|
| Python `Upload` factory | Builds component props from Pydantic `UploadConfig`; exposes a dynamically generated Python signature. [`upload.py`](https://github.com/Ozx-68102/dash-uploader-uppy5/blob/a71c145fa79b7459ffd83002ca301bbe670bde7e/dash_uploader_uppy5/upload.py) |
| Pydantic configuration models | Validate component configuration shape, aliases, option types, file-count relationships, and convert public MB values to bytes. [`models.py`](https://github.com/Ozx-68102/dash-uploader-uppy5/blob/a71c145fa79b7459ffd83002ca301bbe670bde7e/dash_uploader_uppy5/models.py) |
| `configurator` | Stores module-level configuration, creates a handler instance, and registers a POST route. [`configurator.py`](https://github.com/Ozx-68102/dash-uploader-uppy5/blob/a71c145fa79b7459ffd83002ca301bbe670bde7e/dash_uploader_uppy5/configurator.py) |
| TypeScript/React component | Instantiates Uppy and Dashboard, wires Uppy events to Dash props, and provides trigger hooks for upload, retry, cancel, and clear. [`DashUploaderUppy5.tsx`](https://github.com/Ozx-68102/dash-uploader-uppy5/blob/a71c145fa79b7459ffd83002ca301bbe670bde7e/src/components/DashUploaderUppy5.tsx) |
| Uppy transport | Uses Uppy `XHRUpload` to send each file to the configured endpoint as a multipart request. [`createUppy.ts`](https://github.com/Ozx-68102/dash-uploader-uppy5/blob/a71c145fa79b7459ffd83002ca301bbe670bde7e/src/components/utils/createUppy.ts) |
| Flask upload handler | Sanitizes the filename and upload ID, creates a destination folder, saves the uploaded file, and returns a JSON response. [`uploadhandler.py`](https://github.com/Ozx-68102/dash-uploader-uppy5/blob/a71c145fa79b7459ffd83002ca301bbe670bde7e/dash_uploader_uppy5/uploadhandler.py) |
| Build and package system | Uses TypeScript, webpack, generated Dash component bindings, `pnpm-lock.yaml`, `uv.lock`, and `pyproject.toml`. |

### Request and callback flow

1. The Dash app calls `configurator`.
2. The `Upload` factory produces component props; Pydantic validates the prop model.
3. The React component creates one Uppy instance and attaches Dashboard.
4. Uppy applies configured browser restrictions and `XHRUpload` submits a multipart request to the Flask POST route.
5. The handler sanitizes the submitted upload ID and filename, creates the folder, and saves the file.
6. The handler returns JSON with a filename.
7. The Uppy `complete` event maps successful and failed items to Dash component props.
8. Dash callbacks consume `uploadedFiles`, `failedFiles`, and optional trigger status props.

### Useful patterns to consider reusing

- TypeScript for the React component and typed component props.
- A component configuration model with explicit aliases and validation.
- A clear separation between upload-trigger receipt and eventual upload outcome.
- Uppy’s maintained Dashboard UI rather than reimplementing progress and selection UX.
- Lockfiles and declarative `pyproject.toml` metadata.
- Component-level hooks that separate event and trigger behavior.

These are patterns, not blanket endorsements. Their suitability depends on supported runtimes and the new product requirements.

## 3. Comparison and risks to prevent

| Concern | Legacy `dash-uploader` | Uppy5 repository | Required new-project control |
|---|---|---|---|
| Per-app configuration | Shared module-level settings. | Also writes app, folder, URL, and prefixes to shared module-level settings. | Use app-scoped configuration/extension state; test two apps in one process. |
| File path handling | Request-derived identifier and filename participate in path construction without a visible containment check. | Sanitizes names with `basename` and character replacement, but still relies on sanitized client values as storage identifiers. | Use server-generated storage keys; bind session to authorization; enforce resolved-root containment. |
| Authorization | Custom handler hooks are available but default hooks do nothing. | Default upload route has no visible user authorization layer. | Define the host-app authorization contract and enforce it across session creation, data transfer, finalization, and retrieval. |
| Resource limits | Most restrictions live in the browser. | Pydantic config feeds Uppy browser restrictions; the shown handler does not enforce equivalent quotas. | Validate limits in the server protocol and apply request, session, user, and storage quotas. |
| Transport | Custom Flow.js chunks; resumption check disabled. | One multipart XHR request per file; no application-level chunk session or tus protocol is shown. | Select and test a transport based on maximum size, reliability, worker topology, and storage. |
| Finalization | Custom chunk concatenation and lock-file coordination. | `FileStorage.save` writes directly to a target filename. | Stage, verify, and atomically publish; define duplicate/retry semantics. |
| Overwrite behavior | Existing target is removed before writing the assembled file. | A repeated sanitized filename can target the same path and `save` can overwrite it. | Make collision/overwrite behavior an explicit policy; default to non-colliding server keys. |
| Failure responses | Broad exceptions log and then return implicitly. | Exceptions are logged and converted to `abort(500, str(e))`, which may expose internal details. | Return typed, documented errors; keep internal details in protected logs. |
| Component configuration | Hand-written component factory and generated bindings. | Pydantic model plus dynamic public signature. | Validate public configuration, but do not confuse prop validation with request authorization or enforcement. |
| Build reproducibility | Generated `_build` files are absent from the checkout and must be built. | Has `pnpm-lock.yaml` and `uv.lock`; still requires generated component/package build steps. | Prove clean-checkout builds and test the built wheel/sdist in CI. |
| Test evidence | Small suite, mostly browser-oriented. | The inspected tracked file tree contains no test files or test directory. | Make backend protocol/security tests and frontend tests release gates. |
| Runtime scope | Broad old minimums with limited evidence for modern environments. | `requires-python >=3.13`, Dash `>=3.4.0`, which is a narrow Python floor. | Pick a support matrix from user needs and test every declared combination. |

## 4. Main architectural conclusion

Uppy5 improves the browser UI, component language/tooling, and configuration modeling. It does **not** by itself solve the security or reliability concerns inherited from a direct Flask upload endpoint:

- module-global configuration remains;
- browser restrictions are not server-side quotas;
- client-supplied IDs and filenames still influence storage naming;
- the handler directly writes a whole multipart file to its destination;
- there is no visible server-side upload-session state machine or resumable chunk protocol.

The new repository should use Uppy only as a frontend library if it meets the product need. The server-side lifecycle, identity binding, quotas, storage-key design, atomic completion, and cleanup must be specified independently of the UI.

## 5. Proposed non-negotiable controls

1. No module-global mutable app/upload configuration.
2. No client-supplied path becomes a storage path.
3. A client-supplied upload ID is not an authorization credential.
4. Server-enforced size, count, time, and storage limits.
5. Explicit upload-session states and idempotent operations.
6. Staging followed by verified, atomic finalization.
7. Documented error contracts and privacy-aware logs.
8. Backend, protocol, frontend, packaging, and deployment tests in CI.

These controls are elaborated in the [target architecture](./02-target-architecture.md), [requirements](./03-requirements.md), [threat model](./04-security-threat-model.md), and [SDLC plan](./06-sdlc-quality-and-release.md).
