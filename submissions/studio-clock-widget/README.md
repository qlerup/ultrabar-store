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
