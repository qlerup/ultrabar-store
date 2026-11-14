# UltraBar Store - catalog foundation

Community package catalog for [UltraBar Studio](https://github.com/qlerup/ultrabar-studio).
**Not live yet:** Studio 0.14 has app update checks, but does not install store packages.
No test APKs, device credentials or signing keys are published here.

## Distribution

CoreBAR applications are **prebuilt, release-signed APKs** on GitHub Releases.
The user's PC does not compile Android code. The catalog pins exact release
URLs, sizes, checksums, Android package IDs, versionCodes and signer fingerprints.
Each app retains its own license. Apps do not inherit the Studio license.

Planned package families:

| Type | Artifact | Installation |
|---|---|---|
| `corebar-app` | Signed `.apk` | Verified ADB install to chosen CoreBAR |
| `corebar-widget` | Renderer package | Reviewed native widget adapter; initially first-party only |
| `studio-plugin` | Versioned `.zip` | Future Studio host API, separate from Android |

APK updates must retain the original signing key. A checksum is not a substitute
for an Android signing identity. Store refreshes and package versions are
independent of Studio releases once the corresponding installation adapter exists.

## Submissions

Open a pull request with source/build links, package metadata, license,
permissions and compatibility notes. qlerup must review and approve entries
before they go live. Do not publish an unsigned/debuggable APK as production.
Do not add credentials, device serials or signing keys. Package-specific setup
must use a supported host API, not arbitrary install scripts from a manifest.

See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Studio architecture](https://github.com/qlerup/ultrabar-studio/blob/main/docs/store-architecture.md).
The initial catalog is intentionally empty until a package is ready and the
installer exists. `manifest.schema.json` defines the proposed v1 metadata shape;
it does not imply runtime support. Production rollout also requires catalog
validation, trusted release signing and the install checks in the architecture.
