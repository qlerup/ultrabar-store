# Studio Drive Usage

This release uses Studio 0.52.18 or newer. Install the package in Studio. The
package supplies its settings panel, including the available choices, colors
and defaults. Save and Deploy applies each placed card's settings to Core.

One integrated Core widget for PC drive usage. Install this package once in Studio, drag Drive usage onto the bar, choose a drive in the right panel and Deploy. Add multiple copies to show different drives. It uses the same Studio disk renderer as the former System C:, Data D: and All drives cards; these are settings of one widget, not separate apps.

Settings: display name, background color, text color, accent color and Drive (an available PC drive or All drives). A single drive shows percent used, used/total GB and free GB. All drives shows two drives at a time and rotates to the next pair every six seconds on Core when more are available. The Studio preview shows the first pair. It does not aggregate all drives into one total. Defaults to All drives. Drive names and values come from the connected PC, not Core's internal storage.

Requires Studio 0.52.18+, root-enabled ARM32 CB01 and LineOS 1.0.8 or 1.0.9. Keep Studio connected for live PC readings; reconnect Studio after Core restarts. No separate APK or executable is installed by this package. widget.json is the complete declarative source; the shared runtime supplies rendering and collection.

The package itself requests no Android permissions. Studio reads PC drive capacity locally and sends usage metrics to the connected Core. This widget does not read, modify or delete files on those drives.

Validation covered package parsing and editor settings. Both card sizes rendered
on physical CB01 with LineOS 1.0.9 in a temporary mixed layout. Installing a
new package revision and completing Deploy on physical Core are separate
acceptance checks.

Original square 512x512 PNG icon drawn from geometric primitives in make_icon.py; Studio provides rounded corners. Removing the package only removes its library template. Placed cards are removed separately from the layout and with Deploy.

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

In Small size, the card shows one drive label and usage percentage. The large layout includes capacity and can show two drives.

Choose the size under **Widget settings**. With Studio 0.52.1 or newer, hover
over an empty spot in the CoreBAR preview, choose **+**, then select **2×2 grid**.
Dragging the widget into a grid cell selects Small automatically. Small and
mixed layouts require LineOS 1.0.9.
