## Package submission / update

- Package name:
- Package type (`corebar-app`, `corebar-widget`, or `studio-plugin`):
- Publisher (repository owner GitHub account):
- Package ID:
- Your repository: https://github.com/OWNER/REPO
- Stable release: https://github.com/OWNER/REPO/releases/tag/v1.0.0
- Full source commit (40 characters):
- New version:
- Previous approved version (updates only):

## What changes for users?

Describe features, fixes, settings compatibility and hardware requirements.

## Required checklist

- [ ] I own the linked repository and am submitting from that GitHub account.
- [ ] My source is in my own public repository; I control its collaborators and releases.
- [ ] I published a stable release whose tag points to the exact reviewed commit.
- [ ] Added repository.json with repository, commit, release and matching type.
- [ ] Copied exact files for my declared type, icon.png, README.md and LICENSE.
- [ ] manifest.json uses the same source commit, package ID and version.
- [ ] For an update: increased version and retained package/widget IDs and type (or this is a new package).
- [ ] The icon is an original/licensed square static PNG, 256 or 512 pixels, at most 256 KiB.
- [ ] I have rights to distribute all included files and the icon.
- [ ] No secrets, personal device addresses or signing keys are included.
- [ ] I described install/use/update/removal tests and any untested hardware paths below.
- [ ] For an APK: release build, exact permissions, same signing key for updates, complete source.zip matching the pinned commit (or not an APK).
- [ ] For an APK: enabled/exported MAIN/LAUNCHER activity, application DEX, CB01-compatible minSdk and ARM32 native libraries if used (or not an APK).
- [ ] I use only supported Studio fields/runtime/settings; any app-side setup or custom Studio integration requirement is explained in README.md.
- [ ] This PR changes only one submission folder and does not edit catalog.json.
- [ ] I understand that green Actions checks still require Store owner approval.

## Testing and limitations

### Studio settings integration (complete one)

- [ ] Android app with editable Studio settings: follows [APP-SETTINGS.md](https://github.com/qlerup/ultrabar-store/blob/main/APP-SETTINGS.md), settings API 1 and Studio 0.45+; identical studio-settings.json in source/submission/manifest/APK assets; protected StudioSettingsReceiver; actual read/apply confirmation tested.
- [ ] Android app without Studio settings: README explicitly states that settings are configured in the app, not Studio.
- [ ] Native widget/preset: uses the supported widgetApi/pluginApi runtime fields and controls, with the required minimum Studio version.

Settings tested (current-value read, every field, invalid values, apply/confirmation,
restart persistence, upgrade/data preservation, timeout/error):

Special setup/provisioning required (or none):

State explicitly whether this release was tested on physical Core and on which firmware.

## Maintainer publication

Official mirrored download metadata is prepared in the package manifest during review. GitHub generates and publishes the catalog after merge. Do not overwrite an old release asset. Push fixes to this PR to rerun Actions; maintainers can also rerun from Actions > Store submission checks.
