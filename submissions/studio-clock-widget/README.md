# Studio Clock & Date

One integrated widget package for the existing Core bar, not a standalone APK.
Install it once from the Store. It appears in Studio & App Store in the left
library. Drag it onto the bar, edit settings on the right, then Deploy.

Settings: display name, background/text/accent colors, 12/24-hour time, seconds
and date visibility. The clock uses Core's time and locale; Studio previews PC
time and locale. It needs no network or extra Android permissions.

Requires Studio 0.52.0+, root-enabled ARM32 CB01 and LineOS 1.0.8 or 1.0.9.
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

This package owns its Studio controls in `widget.json` -> `widgets[].studio`.
Studio 0.49 renders the versioned, declarative settings descriptor with the same
shared editor used by other packages. Labels, choices, defaults and help belong
to this package; Studio supplies validated controls, draft/Undo/Save/Deploy and
the trusted native renderer. No package-supplied code or script is executed.

Settings belong to each placed block and survive package updates. Package and
widget IDs are unchanged. Existing saved values take precedence over defaults.
The common name and color controls remain supplied by Studio. This is a native
JSON widget, separate from Android settings API 1; there is no Android receiver.

Requirements: https://github.com/qlerup/ultrabar-store/blob/main/APP-SETTINGS.md .
The descriptor is tested against Studio and Store contracts. Physical Core
rendering and the complete Store update/Deploy flow still require owner testing.

## Widget size

In Small size, the clock shows hours and minutes and an optional short date. The large layout includes the configured seconds and full date.

Choose the size in Studio under Widget settings. Mixed sizes require LineOS 1.0.9.
