# Package submissions

Each package must include its own license. By submitting an entry, you confirm
you are authorized to submit it and permit this catalog to publish the supplied
metadata. The referenced package license must permit downloading and installation
by users; mirroring or republishing binaries requires explicit permission.
Submission does not transfer ownership or grant permission to modify Studio.

Required review evidence:
- Source repository and exact source commit; reproducible build instructions.
- Stable package ID, display name, version and supported host/device versions.
- Versioned GitHub Release asset, actual byte length and SHA-256 (no placeholders).
- APK package ID, versionCode and SHA-256 signing certificate fingerprint.
- All permissions, services and device access explained; installation and removal tested.
- No debug builds, embedded credentials, private keys or fixed user device IDs.
- Permission/license text and evidence that you may distribute included components.

qlerup reviews changes before merge. Publication of an entry is separate from
building and signing a binary. Do not run privileged workflows on untrusted PRs.
Signing keys remain in a protected release environment and must be backed up.

## Supported artifacts in Studio 0.18

- `corebar-app`: a release-signed APK with v2 signing, not debuggable. Packages
  in reserved Android/vendor namespaces are rejected. Its metadata and actual
  permissions must match the manifest. Update with the same signing identity.
- `studio-plugin`: a JSON preset pack, at most 64 KiB, containing only `pluginApi`
  and `widgets`. No script or executable plugin API is exposed in this version.
- `corebar-widget`: reserved; installation is not enabled yet.

Approved asset URLs must point to versioned Releases in qlerup/ultrabar-store.
Use a new version and new asset URL for every update. Never replace published
bytes behind an existing manifest hash. The maintainer retains the original
signing keys privately; they are not included in pull requests.
