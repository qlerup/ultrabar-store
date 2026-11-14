## Package submission / update

- Package name:
- Package type (`corebar-app`, `corebar-widget`, or `studio-plugin`):
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
- [ ] This PR changes only one submission folder.
- [ ] I understand that green Actions checks still require Store owner approval.

## Testing and limitations

State explicitly whether this release was tested on physical Core and on which firmware.

## Maintainer publication

Official mirrored download metadata and catalog entry are prepared during review. Do not overwrite an old release asset. Push fixes to this PR to rerun Actions; maintainers can also rerun from Actions > Store submission checks.
