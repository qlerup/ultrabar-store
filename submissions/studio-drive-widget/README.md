# Studio Drive Usage

One integrated Core widget for PC drive usage. Install this package once in Studio, drag Drive usage onto the bar, choose a drive in the right panel and Deploy. Add multiple copies to show different drives. It uses the same Studio disk renderer as the former System C:, Data D: and All drives cards; these are settings of one widget, not separate apps.

Settings: display name, background color, text color, accent color and Drive (an available PC drive or All drives). A single drive shows percent used, used/total GB and free GB. All drives shows two drives at a time and rotates to the next pair every six seconds on Core when more are available. The Studio preview shows the first pair. It does not aggregate all drives into one total. Defaults to All drives. Drive names and values come from the connected PC, not Core's internal storage.

Requires Studio 0.24.0+, root-enabled ARM32 CB01 and LineOS 1.0.8 or 1.0.9. Keep Studio connected for live PC readings; reconnect Studio after Core restarts. No separate APK or executable is installed by this package. widget.json is the complete declarative source; the shared runtime supplies rendering and collection.

The package itself requests no Android permissions. Studio reads PC drive capacity locally and sends usage metrics to the connected Core. This widget does not read, modify or delete files on those drives.

Testing: package and icon validation, existing native disk renderer regression tests and editor browser checks. The new Store installation has not yet been tested by the owner on physical Core. Existing disk cards were already in use on Core; final Store acceptance remains the owner's decision.

Original square 512x512 PNG icon drawn from geometric primitives in make_icon.py; Studio provides rounded corners. Removing the package only removes its library template. Placed cards are removed separately from the layout and with Deploy.

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
Supported controls: drive selection (one drive or all drives), name and colors.
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
