# Bambu for UltraBar Studio

This release uses Studio 0.52.23 or newer. Install the package in Studio. The
package supplies its settings panel, including the available choices, colors
and defaults. Save and Deploy applies each placed card's settings to Core.
H2C and H3C temperature presets use at least two rows.

Bambu LAN printer widgets for CoreBAR. Set up printers in **UltraBar Studio on
your PC**, choose a printer for each widget, then Save and Deploy. Studio sends
live readings to Core through the same channel as CPU, RAM and drive widgets.
No printer setup or companion app is required on Core.

Requires **Studio 0.52.23+**, root-enabled ARM32 CB01 / LineOS 1.0.9, and compatible
Bambu LAN firmware. Keep Studio running for live readings and controls.

## Connect printers

1. Install or update **Bambu** (`studio.bambu`) from Store. Existing placed widgets
   stay in your layout; new users drag the widget onto Core.
2. Select the widget and choose **Manage printers → Add printer** in Studio.
3. Choose the printer model and enter a name, private IPv4 address, serial number and eight-character LAN code.
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

## Print alerts

Enable **Print alert sounds** in the widget settings, then choose **Save** and
**Deploy**. CoreBAR plays different tones for completed prints and printer-reported
print failures or errors. Keep Studio running and connected. It sends the audio
when the printer reports the event. CoreBAR plays it at 80% media volume and
restores the previous level afterwards.

**Wake screen for print alerts** is on by default when sounds are enabled.
Turn it off to play the sounds while leaving the display asleep.

The PC must reach the printer on TLS MQTT port 8883. Find LAN settings on the
printer; some firmware requires LAN mode and Developer Mode for controls. Studio
does not change printer modes. LAN Only may affect Handy/cloud functionality.

## Model presets and display

Choose the model in Manage printers. With UltraBar Studio 0.52.3 or later, the
large home widget and layout preview show a larger model image. If Bambu Studio
is installed on the PC, UltraBar uses its thumbnail for the selected model.
The package illustration is used when the installed thumbnail is unavailable. H2D labels
T0 as Left nozzle and T1 as Right nozzle. Other models keep the reported tool IDs.
Existing connections default to Other until a model is selected. Choosing a model
changes presentation only and does not change printer firmware or capabilities.

Long job filenames scroll on one line in a compact field. Swipe down to close the unfolded widget,
activate its small drag handle, tap outside, or use Back. Horizontal gestures and
ordinary taps still reach printer controls.

## Display and controls

Choose main and secondary readings, details, controls visibility, reduced motion
and 2–5 unfolded slots separately for each widget. Tap the widget on Core to unfold;
on the standard single row, nearby cards shift as it unfolds. In a mixed layout,
printer details open over the cards. Editor previews use
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

Both card sizes rendered on physical CB01 with LineOS 1.0.9 in a temporary
mixed layout. Real H2D/H3C firmware, local discovery, physical Core control
events and the complete Store install → Deploy flow still need hardware acceptance.
No claim is made that every Bambu model or firmware has been physically tested.

## Release

Publish `widget.json` and `icon.png` as immutable stable release assets. Store pins
the source commit, copies exact README/LICENSE/icon/descriptor bytes and mirrors
the reviewed assets with SHA-256 metadata. Studio provides the adaptive temperature layout on Core. After updating Studio, use Save and Deploy.

The original Android build instructions remain in the archived Core-app README.
They are not needed to install or use the Studio widget.

## Package-owned presentation

`widget.json` contains this package's model choices, nozzle labels and vector
artwork through Studio presentation API 1. `artwork/printer_presets.py` regenerates
them. Adding a model or changing artwork/labels is a Bambu package update, without
a Studio code change. The same API is available to other publishers and native
widget kinds; it is not specific to Bambu. Protocol support and new native runtime
behaviors still require an appropriate Studio adapter/runtime update.

## Nozzle details

H3C shows its nine rack positions in a 3 by 3 grid. H2C uses two rows for reported tools. Each tile shows temperature, material and a color swatch when the printer identifies the filament. A dash marks an unknown material. Chamber and bed temperatures each have their own box in the right-hand column. Compact hotend tiles stack their numbered title, temperature, filament material and color. The expanded card leaves space for the rounded corners and places the printer heading and tools side by side. Version 2.8.0 uses the shared panel host in Studio 0.52.23. The widget package defines the expanded layout and print alert melodies. Future changes to those definitions use the same host.

## Widget size

In Small size, the card shows the primary printer reading and print progress. Tap either size to open printer details.

Hover over an empty spot and use **+** to make a 2×2 grid. Drop Bambu into a
grid cell to use the small card. In Studio 0.52.11 or newer, drag it into an
empty large slot to switch back. Earlier Studio versions also have a size
selector in **Widget settings**. Small and mixed layouts require LineOS 1.0.9.

Bambu 2.8.1 defines its printer image choices and model-specific sizing in the package. On a large card the H3C photo matches the cabinet height of the H2D and centers the full printer and AMS beside the print percentage. Image presets require UltraBar Studio 0.52.24 or newer.
