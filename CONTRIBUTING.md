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
