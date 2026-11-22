# Studio Clock & Date

This release uses Studio 0.52.18 or newer. Install the package in Studio. The
package supplies its settings panel, including the available choices, colors
and defaults. Save and Deploy applies each placed card's settings to Core.
The plate and digit colors have separate pickers.

A split-flap clock with paired hour and minute plates. On large cards the optional seconds have their own plate. Only changed plates turn. Dates and AM/PM follow the local clock.

One integrated widget package for the existing Core bar, not a standalone APK.
Install it once from the Store. It appears in the **App Store** group in the Design & actions library. Drag it onto the bar, edit settings on the right, then Deploy.

Settings: display name, background/text/accent colors, 12/24-hour time, seconds
and date visibility. The clock uses Core's time and locale; Studio previews PC
time and locale. It needs no network or extra Android permissions.

Requires Studio 0.52.18+, root-enabled ARM32 CB01 and LineOS 1.0.8 or 1.0.9.
The shared studio-native-v1 runtime is supplied by Studio during Deploy. Keep
Studio connected for runtime restoration after Core restarts. The clock keeps
ticking locally while its renderer remains attached; this is not an independent
Android service or an offline startup guarantee.

widget.json is the complete declarative package source; no compilation is needed.
Studio contains the common editor and Core renderer. No separate presets or APK
need to be installed. Remove from the layout and Deploy to remove it from Core.
Removing the library package alone preserves existing layouts.

Validation covered package parsing and editor settings. Both card sizes rendered
on physical CB01 with LineOS 1.0.9 in a temporary mixed layout. Installing a
new package revision and completing Deploy on physical Core are separate
acceptance checks.

The original app icon is icon.png (512x512 PNG). make_icon.py reproduces it using Pillow; the package license also covers this artwork.

## Releases and maintenance

This repository is the package source of truth. The complete runtime payload is
widget.json; no APK compilation is required. Keep package and widget IDs stable.
Commit changes, test them and publish a new stable GitHub release. Submit updates
through the same Store submission folder with the new version, commit and tag in
manifest.json/repository.json. Eligible updates to registered packages can auto-merge after Store checks. Keep release tags/assets immutable and never commit credentials.
See https://github.com/qlerup/ultrabar-store/blob/main/SUBMIT-A-PACKAGE.md for the
complete submission and update process. The existing package license applies;
public source visibility does not grant permission to create derivative works.

## Studio settings contract

This package owns its Studio controls in `widget.json` -> `widgets[].studio`.
Studio renders the versioned, declarative settings descriptor with the same
shared editor used by other packages. Labels, choices, defaults and help belong
to this package; Studio supplies validated controls, draft/Undo/Save/Deploy and
the trusted native renderer. No package-supplied code or script is executed.

Settings belong to each placed block and survive package updates. Package and
widget IDs are unchanged. Existing saved values take precedence over defaults.
The package declares the color controls. Studio supplies the display name field. This is a native
JSON widget, separate from Android settings API 1; there is no Android receiver.

Requirements: https://github.com/qlerup/ultrabar-store/blob/main/APP-SETTINGS.md .
The descriptor is tested against Studio and Store contracts.

## Widget size

In Small size, the clock shows hours and minutes and an optional short date. The large layout includes the configured seconds and full date.

Choose the size under **Widget settings**. With Studio 0.52.1 or newer, hover
over an empty spot in the CoreBAR preview, choose **+**, then select **2×2 grid**.
Dragging the widget into a grid cell selects Small automatically. Small and
mixed layouts require LineOS 1.0.9.
