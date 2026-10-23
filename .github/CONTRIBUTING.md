# Contributing

Thanks for helping improve `dash-file-uploader`. The project is currently maintained by [@rakrsh](https://github.com/rakrsh).

## Before starting

- Check the existing issues and open an issue before substantial work so the scope can be agreed.
- Keep pull requests focused and link the issue or requirement they address.
- Do not include credentials, private upload data, or other sensitive information in issues, tests, or logs.
- For a suspected vulnerability, follow [SECURITY.md](../SECURITY.md); do not create a public issue.

## Pull requests

Submit changes through a pull request to `main`; do not push directly to the default branch. Include:

- the motivation and user-visible/API impact;
- security, privacy, and operational considerations;
- tests and the exact commands run;
- documentation or migration changes;
- any generated files and how they were generated.

Changes to authorization, upload protocol, storage, limits, dependency policy, generated artifacts, and callback semantics need explicit maintainer review. The repository currently has one maintainer, so an independent approval is not required until a second maintainer is appointed. CI checks will be required once the workflows are established.

## Development checks

The approved toolchain is documented in [the SDLC and release plan](../blueprint/06-sdlc-quality-and-release.md). The repository bootstrap and executable check commands are being established; do not report a check as passing unless it was actually run.

## Generated artifacts

TypeScript/React is the source of truth for the frontend. When the build scaffold is available, regenerate committed Dash bindings and JS/CSS bundles using the documented build command and include the generated changes in the same pull request.

## Conduct

Participation is subject to the [Code of Conduct](../CODE_OF_CONDUCT.md).
