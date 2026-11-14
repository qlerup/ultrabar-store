# Studio Clock 1.0.0

A small offline Android app for CoreBAR displaying device-local time (including
seconds) and today's date. Locale and timezone come from Android. It requests
no permissions, uses no network, runs no background service and does not force
the display to stay awake. It appears in the CoreBAR app list after installation.

This submission is pending owner review. It is not an approved store package
until the catalog pull request is merged.

## Build

JDK plus Android platform 35 and build-tools at `android-15` are required.
Run `build.py --sdk PATH --keystore PATH --password-file PATH --output PATH.apk`.
The signing alias is `studio-clock`. Signing credentials must stay outside Git.
Keep the same signing key for future versions; changing it prevents in-place
Android updates. The produced APK is release-signed, not debuggable.

## License

Copyright (c) 2026 qlerup. All rights reserved. You may download, install and run
the unmodified official release on your own authorized devices. Modifications,
derivative works and redistribution require written permission. Mandatory legal
rights and GitHub viewing/forking rights are unaffected. Provided as is, without
warranty to the extent permitted by law.
