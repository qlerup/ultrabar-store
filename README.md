# UltraBar Store

Reviewed apps and plugins for [UltraBar Studio](https://github.com/qlerup/ultrabar-studio).
Studio 0.18+ reads `catalog.json` from **main** when the Store opens, on Refresh,
and once per minute while visible. Merging an approved catalog entry makes it
available without a Studio update. Installation remains the user's choice.

## Submitting a package

1. Fork this repository and create a branch for your submission.
2. Add a folder under `submissions/` with source/build instructions, README,
   license, permissions, compatibility information and `manifest.json`.
3. Supply a prebuilt release-signed APK, or a declarative Studio plugin JSON.
   The maintainer publishes reviewed binaries as versioned assets in this
   repository's Releases. Do not commit binaries or signing keys to Git.
4. Add the manifest to `catalog.json` with the real asset URL, size and SHA-256.
   APKs also require package ID, versionCode, minSdk and signer SHA-256.
5. Open a pull request. **qlerup reviews it before merge.** Until merge, the
   submission is not visible in Studio's approved catalog.

CoreBAR apps are prebuilt APKs; Studio does not compile code on users' PCs.
The installer checks the approved artifact hash, APK metadata, permissions and
signing certificate identity. Android verifies the signature and enforces update
signer continuity. Apps never receive credentials or root access from the store.

Studio plugins currently use a JSON file with `pluginApi: 1` and a `widgets`
array. Each widget has `name` and `kind` (`clock`, `cpu`, `memory`, `gpu`, `disk`),
with optional hex `background`, `textColor` and `accent` values. No scripts,
executables, shell commands or new permissions are allowed. Installed presets
appear in Widget library > Studio & App Store. Adding/deploying is explicit.
Native DEX renderer packages and executable Windows plugins are not supported.

See [CONTRIBUTING.md](CONTRIBUTING.md), [manifest.schema.json](manifest.schema.json)
and the examples under `submissions/`. Each submitted app retains its own license.

## Review packages

Release assets labelled as review builds are available for inspection but do not
become approved store entries until their catalog pull request is merged.
Android app signing keys must be preserved privately for later updates.
