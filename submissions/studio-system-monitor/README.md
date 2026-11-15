# Studio System Monitor

One Store installation adds one System Monitor widget to the library. Drag it onto the bar and choose Show: CPU usage, RAM usage or GPU usage in the right panel, then Deploy. Add multiple blocks and choose independently for each block. The library continues to list one template.

CPU shows Windows processor utilization. RAM shows utilization and used/total memory. GPU shows NVIDIA GPU utilization and used/total video memory through nvidia-smi; currently only the first returned GPU is used. AMD/Intel and machines without nvidia-smi have no GPU readings. Missing sensors show unavailable rather than fabricated zeroes. CPU needs two samples to calculate usage. These values describe the PC, not Core's internal hardware.

Each block supports its own Show choice, display name, background color, text color and accent color. There are no executable scripts in this package. widget.json is the complete source; Studio's shared native runtime supplies the data collection, renderer and settings.

Requires Studio 0.24.0+, root-enabled ARM32 CB01 and LineOS 1.0.8 or 1.0.9. Keep Studio connected for live metrics; reconnect after Core restarts. No separate APK is installed. Package requests no Android permissions. Studio reads performance counters locally and sends metrics to the selected Core; no file contents are read by these widgets.

Testing: live PC measurements confirmed for CPU, RAM and NVIDIA GPU; existing native renderer regression checks; browser checks for adding multiple cards, unique library entries and settings/save. The new Store install/deploy flow still requires owner testing on physical Core. Do not interpret live PC measurements as proof of physical Core rendering.

Original square 512x512 app icon is drawn with geometric primitives by make_icon.py. Studio applies the corner mask. Removing the package removes the library templates; placed cards are removed separately from the layout and with Deploy.

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
Supported controls: CPU/RAM/GPU measurement choice per block, name and colors.
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
