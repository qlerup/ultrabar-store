# Studio System Monitor

One Store installation adds one System Monitor widget to the library. Drag it onto the bar and choose Show: CPU usage, RAM usage or GPU usage in the right panel, then Deploy. Add multiple blocks and choose independently for each block. The library continues to list one template.

CPU shows Windows processor utilization. RAM shows utilization and used/total memory. GPU shows NVIDIA GPU utilization and used/total video memory through nvidia-smi; currently only the first returned GPU is used. AMD/Intel and machines without nvidia-smi have no GPU readings. Missing sensors show unavailable rather than fabricated zeroes. CPU needs two samples to calculate usage. These values describe the connected Windows PC. Studio 0.52.2 refreshes live readings while the layout preview is visible.

Each block supports its own Show choice, display name, background color, text color and accent color. There are no executable scripts in this package. widget.json is the complete source; Studio's shared native runtime supplies the data collection, renderer and settings.

Requires Studio 0.52.0+, root-enabled ARM32 CB01 and LineOS 1.0.8 or 1.0.9. Keep Studio connected for live metrics; reconnect after Core restarts. No separate APK is installed. Package requests no Android permissions. Studio reads performance counters locally and sends metrics to the selected Core; no file contents are read by these widgets.

Validation covered package parsing and editor settings. Both card sizes rendered
on physical CB01 with LineOS 1.0.9 in a temporary mixed layout. Installing a
new package revision and completing Deploy on physical Core are separate
acceptance checks.

Original square 512x512 app icon is drawn with geometric primitives by make_icon.py. Studio applies the corner mask. Removing the package removes the library templates; placed cards are removed separately from the layout and with Deploy.

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
The common name and color controls remain supplied by Studio. This is a native
JSON widget, separate from Android settings API 1; there is no Android receiver.

Requirements: https://github.com/qlerup/ultrabar-store/blob/main/APP-SETTINGS.md .
The descriptor is tested against Studio and Store contracts.

## Widget size

In Small size, the card shows the selected measurement and its usage percentage. The large layout includes additional sensor details.

Choose the size under **Widget settings**. With Studio 0.52.1 or newer, hover
over an empty spot in the CoreBAR preview, choose **+**, then select **2×2 grid**.
Dragging the widget into a grid cell selects Small automatically. Small and
mixed layouts require LineOS 1.0.9.
