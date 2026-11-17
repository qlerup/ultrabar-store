# Bambu for UltraBar Studio

Bambu LAN printer widgets for CoreBAR. Set up printers in **UltraBar Studio on
your PC**, choose a printer for each widget, then Save and Deploy. Studio sends
live readings to Core through the same channel as CPU, RAM and drive widgets.
No printer setup or companion app is required on Core.

Requires **Studio 0.49.2+**, root-enabled ARM32 CB01 / LineOS 1.0.9, and compatible
Bambu LAN firmware. Keep Studio running for live readings and controls.

## Connect printers

1. Install or update **Bambu** (`studio.bambu`) from Store. Existing placed widgets
   stay in your layout; new users drag the widget onto Core.
2. Select the widget and choose **Manage printers → Add printer** in Studio.
3. Enter a name, private IPv4 address, serial number and eight-character LAN code.
   **Search local network** can fill the address and serial. Enter the code yourself.
4. Choose **Check connection**, compare the SHA-256 fingerprint with a trusted
   connection to the printer, then **Trust certificate & save**. No access code is
   sent before approval. Later connections require that exact certificate.
5. Select a printer in each widget's **Printer** dropdown, then Save and Deploy.

Up to 16 printers can be saved. Widgets can follow different printers at the same
time, or show different readings for one printer. Connection changes save
immediately on the PC. Widget selections follow the normal draft/Undo/Save/Deploy
workflow. **Manage printers** also supports editing, removal and explicit reconnect.
Status updates automatically while the dialog is open, without resetting the form.
A blank code keeps the saved code only for the same address and serial.

The PC must reach the printer on TLS MQTT port 8883. Find LAN settings on the
printer; some firmware requires LAN mode and Developer Mode for controls. Studio
does not change printer modes. LAN Only may affect Handy/cloud functionality.

## Display and controls

Choose main and secondary readings, details, controls visibility, reduced motion
and 2–5 unfolded slots separately for each widget. Tap the widget on Core to unfold;
neighboring cards move temporarily and return when closed. Editor previews use
clearly marked sample data.

Live readings include print progress, job, remaining time, layers and reported
nozzle/bed/chamber temperatures, including packed multi-extruder reports.
The unfolded widget gives every reported nozzle its own temperature in °C.
It adjusts the layout to fit the number of nozzles, including nine on the H3C.
Pause/resume/stop/chamber-light controls default off per connection. They require
explicit enablement in Studio, fresh state and compatible firmware. Stop asks for
confirmation on Core. Stale state, disconnects or signed-command enforcement
disable controls. Commands are never replayed after reconnect. Printer telemetry
must confirm success; after a timeout check the physical printer before retrying.

Camera streaming, cloud login, uploads, starting jobs, heating, AMS operations and
laser/tool-changing functions are not implemented. This is an independent community
project, unaffiliated with Bambu Lab or the UltraBARX manufacturer.

## Privacy and architecture

Studio owns the MQTT connections and protects saved credentials with Windows
DPAPI under the current Windows account. Credentials never enter layout drafts,
exports or Core's metrics file. Core receives bounded, sanitized readings keyed
by opaque printer IDs. No cloud account, analytics or external service is used.
First-use certificate trust still requires a trusted comparison; it cannot establish
printer identity on a hostile network by itself.

The Store artifact is the data-only root `widget.json`; it contains no executable
code or credentials. Its versioned `widgets[].studio` descriptor owns display
fields, labels, choices, defaults, help and the printer connection form. Studio
provides the shared settings/connection UI, automatic status lifecycle, protected
storage and approved `bambu-lan` provider. Other packages use this same contract.
Changing labels or supported defaults does not require a custom Studio dialog.
Protocol support and new providers still require a trusted Studio implementation. The trusted connection service and native renderer ship in
[UltraBar Studio](https://github.com/qlerup/ultrabar-studio). This repository keeps
the original icon, widget descriptor and native renderer reference source.

## Previous Core app

Release 1.x was the `studio.bambu` Android app. Release 2.1.0 retains that same
Store identity and appears as **Update** for existing installations. Studio 0.49.0
keeps placed cards, names, colors, readings and display settings, and removes their
obsolete companion dependency. Set up and select printer connections in Studio,
then Save and Deploy. Credentials on Core are not silently extracted or deleted.
The briefly published `studio.bambu.widget` registration is also consolidated into
`studio.bambu` when updated; it is not a second product. Uninstall the old APK
separately when no longer needed.
The original app source remains available; its documentation is archived in
[CORE-APP-LEGACY.md](docs/CORE-APP-LEGACY.md).

## Validation

Studio tests cover Windows encrypted storage, two independent printer selections,
MQTT bounds, fake-printer TLS sessions, certificate approval and changes, status
freshness, control gates and corresponding telemetry confirmation. Browser tests
cover setup, desktop/mobile layouts, Save and Undo. Native geometry and D8 build
checks cover liquid widgets.

Real H2D/H3C firmware, discovery on the owner's network, physical Core control
events and the complete Store install → Deploy flow still need hardware acceptance.
No claim is made that every Bambu model or firmware has been physically tested.

## Release

Publish `widget.json` and `icon.png` as immutable stable release assets. Store pins
the source commit, copies exact README/LICENSE/icon/descriptor bytes and mirrors
the reviewed assets with SHA-256 metadata. Studio 0.49.2+ provides the adaptive
temperature layout on Core. After updating Studio, use Save and Deploy.

The original Android build instructions remain in the archived Core-app README.
They are not needed to install or use the Studio widget.
