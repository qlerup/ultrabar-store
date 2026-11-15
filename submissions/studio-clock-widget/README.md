# Studio Clock & Date

One integrated widget package for the existing Core bar, not a standalone APK.
Install it once from the Store. It appears in Studio & App Store in the left
library. Drag it onto the bar, edit settings on the right, then Deploy.

Settings: display name, background/text/accent colors, 12/24-hour time, seconds
and date visibility. The clock uses Core's time and locale; Studio previews PC
time and locale. It needs no network or extra Android permissions.

Requires Studio 0.20.0+, root-enabled ARM32 CB01 and LineOS 1.0.8 or 1.0.9.
The shared studio-native-v1 runtime is supplied by Studio during Deploy. Keep
Studio connected for runtime restoration after Core restarts. The clock keeps
ticking locally while its renderer remains attached; this is not an independent
Android service or an offline startup guarantee.

widget.json is the complete declarative package source; no compilation is needed.
Studio contains the common editor and Core renderer. No separate presets or APK
need to be installed. Remove from the layout and Deploy to remove it from Core.
Removing the library package alone preserves existing layouts.

Validation: package parser and no-device-write installation tests; browser
library drag/settings/save flow; native Java renderer compiles. Actual clock
rendering and final Deploy on physical Core still require owner testing.

The original app icon is icon.png (512x512 PNG). make_icon.py reproduces it using Pillow; the package license also covers this artwork.

## Releases and maintenance

This repository is the package source of truth. The complete runtime payload is
widget.json; no APK compilation is required. Keep package and widget IDs stable.
Commit changes, test them and publish a new stable GitHub release. Submit updates
through the same Store submission folder with the new version, commit and tag in
manifest.json/repository.json. The Store owner reviews each version before it
becomes available. Keep release tags/assets immutable and never commit credentials.
See https://github.com/qlerup/ultrabar-store/blob/main/SUBMIT-A-PACKAGE.md for the
complete submission and update process. The existing package license applies;
public source visibility does not grant permission to create derivative works.

## Studio settings contract

This package uses widgetApi 1 and the studio-native-v1 declarative runtime.
Supported controls: time format, seconds/date visibility, name and colors.
Settings belong to each placed block and are saved with the Studio profile/draft;
Deploy applies them to Core. Existing widget/package IDs remain unchanged.
It is a native JSON widget, not an APK: it must not contain an Android receiver
or an APK settings descriptor. Studio provides the renderer and validates the
supported widget fields. No package-supplied code or install script is executed.

Requirements: https://github.com/qlerup/ultrabar-store/blob/main/APP-SETTINGS.md .
This documentation update leaves widget.json unchanged. The package is checked
against the runtime validator and existing Studio regression suite. Physical
rendering was not retested for this documentation-only update; test existing
placed blocks and persistence when reviewing.
