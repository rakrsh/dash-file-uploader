# Support policy

## Supported environments

The supported Python, Dash, browser, and build-tool versions are listed in [the SDLC and release plan](blueprint/06-sdlc-quality-and-release.md). A version is supported only when the project validates it through the documented compatibility process.

## Supported project releases

- **Before 1.0:** only the latest published release is supported. Earlier releases may receive no fixes, including security fixes.
- **From 1.0 onward:** the latest minor release line is fully supported. The immediately preceding minor line receives security fixes for six months after it is superseded, subject to the affected version being in the published support matrix.
- Only the latest patch release in a supported line is eligible for fixes. Users should upgrade to the latest patch.
- Pre-releases and development builds are not supported for production use.

The project does not provide a response-time or resolution-time SLA. Support and defect reports should be filed through GitHub issues. Do not use public issues for security reports; follow [SECURITY.md](SECURITY.md).

## End of support

A minor line leaves support six months after the next minor line supersedes it. The latest supported line may change when a new release is published. End-of-support notices will be included in release notes and the changelog.
