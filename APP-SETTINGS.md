# Required Studio settings integration

Use this specification when an Android app exposes editable settings in Studio.
Requires **Studio 0.45.0**, root-enabled CB01 ADB and **settings API 1**.
Apps without Studio settings may omit the integration, but must say so in their
README and PR. Native JSON widgets use the separate runtime described below.

## Mandatory files and Android component

1. Include `studio-settings.json` in your upstream repository root and Store
   submission folder. Its JSON must equal `manifest.json` -> `settings`.
2. Embed that exact JSON as **assets/studio-settings.json inside app.apk**.
   Gradle projects normally use `src/main/assets/studio-settings.json`.
3. Implement `<your Android package>.StudioSettingsReceiver` and declare:

```xml
<receiver android:name=".StudioSettingsReceiver"
          android:enabled="true" android:exported="true"
          android:permission="android.permission.DUMP" />
```

This sender permission restricts notification to trusted ADB/root callers. Do not
request DUMP as an app permission or expose an unprotected settings receiver.
Keep its class name when shrinking code. Keep the enabled/exported MAIN/LAUNCHER
activity also required by Studio. No arbitrary component names or transports.

4. Set `compatibility.minStudioVersion` to **0.45.0 or later**, `hostApi` to 1,
   and put the descriptor below in the package manifest's `settings` property.
5. Include all normal APK submission files: signed app.apk, pinned source.zip,
   icon.png, README.md, LICENSE, manifest.json and repository.json. The public
   source repository also needs AndroidManifest.xml at root and build instructions.

## Descriptor and supported fields

```json
{
 "api":1,
 "fields":[
  {"key":"enabled","label":"Enabled","type":"boolean","default":true},
  {"key":"delay","label":"Delay (ms)","help":"Wait before activating.",
   "type":"integer","default":1000,"min":0,"max":3000,"step":250}
 ]
}
```

Only `api` and `fields` are allowed. Use integer API 1 and 1-32 fields, within
32 KiB. Every field needs stable unique `key`, `label`, `type` and valid `default`.
Keys match `[a-zA-Z][a-zA-Z0-9_]{0,63}`. Labels contain 1-100 characters; optional
`help` contains 1-500. Descriptions are plain text. Unknown properties are rejected.

| Type | Additional required properties | Values |
| --- | --- | --- |
| boolean | None | JSON true/false |
| integer | Integer min/max/positive step | Integer in range, aligned to step from min |
| number | Finite min/max/positive step | Finite number in range, aligned to step from min |
| string | maxLength, 1-2048 | Text without control characters |
| url | maxLength, 1-2048 | Absolute HTTP/HTTPS URL with host, without credentials |
| choice | options, 1-32 objects with unique string value and label | A declared value |

Numeric bounds are limited to +/- 10^12. Booleans are not integers. Properties for
another type are rejected. Empty string values are allowed; empty URLs are not.
Do not use this API for credentials, tokens, file paths, shell commands, scripts
or downloaded executable code. It is not a secret storage or provisioning API.

## Required read/apply/confirmation behavior

Settings belong to the app on Core and apply across profiles. Studio edits stay
in the local draft until Save/Deploy. **Read settings from Core** loads actual
current app values into that draft; displayed defaults are not a device read.

Studio atomically writes UTF-8 JSON in app-private storage:
`getFilesDir()/ultrabar-studio/request.json`, app UID ownership and mode 600.
After verifying bytes it broadcasts explicitly to `.StudioSettingsReceiver`,
action `<packageId>.STUDIO_SETTINGS`.

```json
{"api":1,"revision":"0123456789abcdef0123456789abcdef","operation":"read"}
```

For `operation: "apply"`, the request also contains `values` with **all** declared
keys and valid values. Reject unknown keys and invalid types/ranges. The revision
is a fresh 32-character lowercase hexadecimal request ID. Validate the complete
request before applying it, save durably, then notify your own runtime. Preserve
unrelated existing settings and user data.

Atomically write `getFilesDir()/ultrabar-studio/response.json`:

```json
{"api":1,"revision":"0123456789abcdef0123456789abcdef","status":"ok",
 "values":{"enabled":true,"delay":1000}}
```

Return **actual saved values**, not an echo, for both read and apply. On failure
return matching api/revision and `status: "error"`. Requests/responses are at most
32 KiB. Studio requires the matching revision, all valid fields and, for apply,
exact requested values. It waits roughly five seconds plus bounded ADB calls.
Stale/missing/rejected replies fail Deploy. Changes may already have happened;
Studio preserves the draft/backup and instructs the user to read back before
retrying. Confirmation covers settings persistence, not overall app functionality.

## Complete example

[examples/settings-app](examples/settings-app) supplies all six field types,
Android manifest, receiver adapter, build script and reusable
`StudioSettingsBridge.java`, under MIT. Copy into your own repository, change
package ID and implement `readValues`/`applyValues` for your actual app storage.
The helper bounds/validates requests and writes atomic responses. Keep signing
keys private. Store/Studio never execute a contributor's build or install script.

Vivo Screen Sync 1.1 uses the same helper with its existing sync preferences.
Its bridge credential provisioning remains a trusted Studio integration;
declaring fields cannot grant credentials or custom setup commands.

## Native widget panels (Studio 0.49+)

Native widgets can own their Studio settings interface in each `widget.json`
widget's optional `studio` descriptor. This is separate from Android app settings
API 1: do not add a receiver or APK `settings` property to JSON widget manifests.
The package owns labels, choices, defaults, help and connection field presentation.
Studio owns rendering, validation, drafts/Undo/Save/Deploy, protected secrets,
automatic status updates and approved local connection providers. No package
HTML, JavaScript, Python, commands, arbitrary URLs or executable plugins run.

### Implement a native app-owned panel

1. Put `widget.json` at your source repository root using integer `widgetApi: 1`,
   `runtime: "studio-native-v1"` and stable widget IDs. Choose a renderer already
   supported by Studio. This is the entire data-only native package; no APK,
   receiver, custom JavaScript or PC installation step is required.
2. Add `studio: {"api":1,...}` to each widget that needs a panel. Under `settings`,
   declare `api: 1` and `fields` with stable supported keys, labels, types and
   defaults. Add optional plain-text `help`. The shared renderer handles field
   controls and validation. Existing saved values override defaults.
3. Keep top-level runtime defaults aligned with the panel defaults. Keep existing
   widget/package IDs and field meanings stable when updating. Studio handles
   common display name/background/text/accent controls; do not duplicate them.
4. If needed, declare an approved dynamic source or connection provider using the
   complete examples below. A new protocol requires a reviewed Studio adapter;
   adding a provider name or extra field in JSON cannot implement it.
5. Set the Store manifest minimum to Studio **0.49.0** and test the actual user
   flow. Publish/pin the upstream release before copying exact files to Store.

Complete `widget.json` for a clock with all of its app-owned controls:

```json
{
  "widgetApi": 1,
  "runtime": "studio-native-v1",
  "widgets": [
    {
      "id": "clock",
      "name": "Clock & date",
      "kind": "clock",
      "background": "#192325",
      "textColor": "#eef6f2",
      "accent": "#b8adff",
      "hourFormat": "24",
      "showSeconds": true,
      "showDate": true,
      "studio": {
        "api": 1,
        "help": "Uses Core time and locale; editor preview uses PC time. Keep Studio connected to restore the widget after Core restarts.",
        "settings": {
          "api": 1,
          "fields": [
            {
              "key": "hourFormat",
              "label": "Time format",
              "type": "choice",
              "default": "24",
              "options": [
                {
                  "value": "12",
                  "label": "12-hour"
                },
                {
                  "value": "24",
                  "label": "24-hour"
                }
              ]
            },
            {
              "key": "showSeconds",
              "label": "Show seconds",
              "type": "boolean",
              "default": true
            },
            {
              "key": "showDate",
              "label": "Show date",
              "type": "boolean",
              "default": true
            }
          ]
        }
      }
    }
  ]
}
```

In the package `manifest.json`, retain the normal required metadata and declare:

```json
{"type":"corebar-widget","compatibility":{"minStudioVersion":"0.49.0",
 "hostApi":1,"models":["CB01"],"abis":["armeabi-v7a"],
 "lineosVersions":["1.0.9"]},"permissions":[]}
```

This is a manifest fragment, not a complete submission. Only declare hardware/
firmware you have tested. An APK carrying bundled native `studio` descriptors
also requires Studio 0.49.0; the old bundle minimum of 0.46.0 is insufficient.

Declare `compatibility.minStudioVersion` **0.49.0 or later**. See
[widget-studio.schema.json](widget-studio.schema.json); the trusted
`scripts/widget_studio_contract.py` checks renderer-specific supported fields,
types and choices. Descriptors are at most 32 KiB, plain text only. Settings use
the field types and bounds above; authors should align declared defaults with
the widget runtime defaults. Existing saved values override defaults. Stable keys and widget
IDs preserve placed cards. Studio continues to supply common names/colors.

### Supported settings by renderer

| Renderer `kind` | Field keys and exact types | Supported values |
| --- | --- | --- |
| `clock` | `hourFormat`: choice; `showSeconds`, `showDate`: boolean | `hourFormat` choices `12`, `24` |
| `cpu`, `memory`, `gpu` | `kind`: choice | `cpu`, `memory`, `gpu`; choices must stay within the widget's top-level `kindOptions` |
| `disk` | `drive`: string, maxLength 128 | `all` or an uppercase Windows drive root such as `C:\`; approved live source below |
| `bambu` | `primary`: choice | `progress`, `state`, `remaining`, `temperature` |
| `bambu` | `secondary`: choice | `remaining`, `state`, `job`, `layers`, `temperature`, `none` |
| `bambu` | `expandedSlots`: integer | min/max within 2-5, positive step, default aligned to step |
| `bambu` | `showJob`, `showTemperatures`, `showLayers`, `showRemaining`, `showControls`, `liquidMotion`: boolean | true/false |

A panel may expose a supported subset. Choice options carry stable string values
and package-owned labels. Other fields cannot introduce unsupported runtime
behavior. Do not rename existing saved keys to change a label.

### Live PC drive choices

Use the approved `pc.drives` capability to populate the drive control. The source
is a fixed capability identifier, not a URL, code module or command. Studio offers
All drives, current PC drive roots and the saved value even if unavailable. A
complete drive package looks like this:

```json
{
  "widgetApi": 1,
  "runtime": "studio-native-v1",
  "widgets": [
    {
      "id": "drive-usage",
      "name": "Drive usage",
      "kind": "disk",
      "background": "#192325",
      "textColor": "#eef6f2",
      "accent": "#94d9bb",
      "studio": {
        "api": 1,
        "help": "All drives shows two drives at a time and rotates to the next pair every six seconds on Core. The editor preview shows the first pair. Values describe this PC.",
        "sources": {
          "drive": "pc.drives"
        },
        "settings": {
          "api": 1,
          "fields": [
            {
              "key": "drive",
              "label": "Drive",
              "type": "string",
              "maxLength": 128,
              "default": "all"
            }
          ]
        }
      }
    }
  ]
}
```

### Printer connection panel and trusted provider

A Bambu panel may declare `connection` with exactly `provider`, `key`, `label`,
`title`, `manageLabel`, `itemLabel`, `setupHelp`, `fields`. The supported provider
is `bambu-lan`, selection key `printerId`. Its five fields are `name`, `host`,
`serial` (type `string`), `code` (type `secret`), `controls` (type `boolean`). Each
has `key`, `label`, `type`, optional boolean `required`, optional plain-text `help`,
and required nonboolean `maxLength` 1-2048. The provider enforces protocol limits
independently of presentation. Secrets never enter drafts, exports or Core metrics.
The shared connection dialog refreshes status automatically and preserves form
input/focus; closing it stops refresh. New protocols require a trusted Studio
provider implementation; a descriptor cannot grant network access or code execution.

Complete Bambu package example; copy the provider keys/types exactly and customize
labels/help/defaults only within the supported contract:

```json
{
  "widgetApi": 1,
  "runtime": "studio-native-v1",
  "widgets": [
    {
      "id": "bambu-liquid",
      "name": "Bambu",
      "kind": "bambu",
      "background": "#14202b",
      "textColor": "#eff6fa",
      "accent": "#86e4c3",
      "primary": "progress",
      "secondary": "remaining",
      "expandedSlots": 3,
      "showJob": true,
      "showTemperatures": true,
      "showLayers": true,
      "showRemaining": true,
      "showControls": true,
      "liquidMotion": true,
      "studio": {
        "api": 1,
        "settings": {
          "api": 1,
          "fields": [
            {
              "key": "primary",
              "label": "Main reading",
              "type": "choice",
              "default": "progress",
              "options": [
                {
                  "value": "progress",
                  "label": "Print progress"
                },
                {
                  "value": "state",
                  "label": "Printer status"
                },
                {
                  "value": "remaining",
                  "label": "Time remaining"
                },
                {
                  "value": "temperature",
                  "label": "Nozzle temperature"
                }
              ]
            },
            {
              "key": "secondary",
              "label": "Secondary reading",
              "type": "choice",
              "default": "remaining",
              "options": [
                {
                  "value": "remaining",
                  "label": "Time remaining"
                },
                {
                  "value": "state",
                  "label": "Printer status"
                },
                {
                  "value": "job",
                  "label": "Job name"
                },
                {
                  "value": "layers",
                  "label": "Layer count"
                },
                {
                  "value": "temperature",
                  "label": "Nozzle temperature"
                },
                {
                  "value": "none",
                  "label": "None"
                }
              ]
            },
            {
              "key": "expandedSlots",
              "label": "Size when unfolded",
              "type": "integer",
              "default": 3,
              "min": 2,
              "max": 5,
              "step": 1
            },
            {
              "key": "showJob",
              "label": "Job name",
              "type": "boolean",
              "default": true
            },
            {
              "key": "showTemperatures",
              "label": "Temperatures",
              "type": "boolean",
              "default": true
            },
            {
              "key": "showLayers",
              "label": "Layer count",
              "type": "boolean",
              "default": true
            },
            {
              "key": "showRemaining",
              "label": "Time remaining",
              "type": "boolean",
              "default": true
            },
            {
              "key": "showControls",
              "label": "Printer controls",
              "type": "boolean",
              "default": true
            },
            {
              "key": "liquidMotion",
              "label": "Liquid unfold animation",
              "type": "boolean",
              "default": true
            }
          ]
        },
        "connection": {
          "provider": "bambu-lan",
          "key": "printerId",
          "label": "Printer",
          "title": "Bambu printers",
          "manageLabel": "Manage printers",
          "itemLabel": "printer",
          "setupHelp": "Find the IP, serial and LAN access code in the printer network settings. The PC and printer need LAN access. Some firmware requires Developer Mode for controls.",
          "fields": [
            {
              "key": "name",
              "label": "Printer name",
              "type": "string",
              "maxLength": 48,
              "required": true
            },
            {
              "key": "host",
              "label": "Printer IP address",
              "type": "string",
              "maxLength": 48,
              "required": true
            },
            {
              "key": "serial",
              "label": "Printer serial number",
              "type": "string",
              "maxLength": 32,
              "required": true
            },
            {
              "key": "code",
              "label": "8-character LAN access code",
              "type": "secret",
              "maxLength": 8,
              "required": true
            },
            {
              "key": "controls",
              "label": "Enable pause, resume, stop and light",
              "type": "boolean",
              "required": false
            }
          ]
        },
        "help": "Display preferences apply to this widget. Printer connections and access codes stay on this PC. Enable controls in Manage printers. Unfolding moves neighboring cards, then restores them on close."
      }
    }
  ]
}
```

The trusted `bambu-lan` adapter implements LAN discovery, a credential-free TLS
certificate probe, certificate approval/pinning, saved connections, explicit
reconnect, connection status and bounded printer telemetry/control. A package
selects this adapter; it does not supply networking code. Adding another device
protocol requires a Studio change implementing/registering that provider, contract
validation, tests and capability handling; after that packages can use its shared
panel without adding another custom editor form.

Users enter a private printer IP, serial and eight-character LAN code. The probe
must send no MQTT credentials. Show the returned SHA-256 fingerprint, require a
comparison with a trusted printer connection and explicit approval before saving
or sending credentials. Later connections require the pinned certificate. The
provider validates fields independently of the package's display lengths. A blank
code when editing retains the existing secret only for unchanged address/serial.
Connection changes persist immediately on the PC; only the opaque selected
`printerId` belongs in each widget draft. Never place the access code, host/serial
or certificate pin in the layout, descriptor, export or metrics sent to Core.

### Settings scope and lifecycle

| Integration | Owner and scope | Apply behavior |
| --- | --- | --- |
| Native `widgets[].studio.settings` | Package defines fields; values belong to each placed widget/profile | Draft, Undo and Save preserve values; Deploy applies the layout/runtime settings |
| Native `studio.connection` | Approved provider owns PC connection records/secrets; Bambu saved printers are shared by widgets/packages using `bambu-lan` | Connection edits save immediately; each widget independently chooses an opaque record ID |
| Android manifest `settings` API 1 | Android app owns actual app-private global values across profiles | Read loads actual Core values; Deploy applies and requires receiver confirmation |

Studio supplies the same connection dialog lifecycle for every supported provider:
status refresh while open, no form resets or lost focus during refresh, visible
errors and refresh cleanup when closed. The app descriptor owns presentation; the
trusted provider owns operational validation and secrets. Package-scoped endpoint
authorization does not create separate credential stores: the built-in Bambu
adapter reuses the shared PC saved-printer store across packages. A hidden controls field
or a claimed default cannot bypass the provider's action gates.

### Developer verification checklist

- Validate the descriptor and normal package files before publishing. From a
  checkout of the Store repository with the new contract available:

  ```sh
  python -m pip install Pillow==12.3.0
  python -m unittest discover -s scripts -p "test_*.py"
  python -c "from pathlib import Path; import sys; sys.path.insert(0,'scripts'); from validate import widget_package; widget_package(Path('../my-widget/widget.json').read_bytes()); print('widget.json OK')"
  python scripts/validate.py . --generated-catalog --verify-assets
  ```

  Replace `../my-widget/widget.json` with your source descriptor. The complete
  Store-tree check also inspects existing APK submissions and requires trusted
  Android `aapt`/`apksigner` tools (`ANDROID_BUILD_TOOLS` pointing at their installed
  build-tools directory). These commands validate data and published bytes; they
  do not execute submitted app code. Do not edit generated `catalog.json`.
- In Studio 0.49+, install, drag and edit two copies independently. Verify every
  label/choice/help, dynamic options, defaults, Save/reload, Undo and Deploy.
- Upgrade an existing package and confirm placed IDs, colors, values and layout
  persist. Test missing sensors/drives, unavailable connections and uninstall.
- For providers, test discovery/no results, probe/fingerprint approval, changed
  certificate rejection, saved/reloaded secrets, blank-secret edit, reconnect,
  automatic Connected/Disconnected updates, request errors and closing/reopening
  the panel. Confirm partially entered form values and keyboard focus survive
  refresh. Test that two package instances independently select the provider's
  shared records and that secret values never enter API responses or drafts.
- For Android API 1, perform the receiver read/apply/confirmation/persistence and
  invalid-request tests described above; native per-widget JSON is not a substitute.
- Test physical Core and real devices for the supported matrix. State exactly
  which paths were simulated, statically checked or remain untested in the PR.
- Publish a new immutable upstream version, update the manifest version/minimum,
  pin its full commit/tag, copy exact release files, update SHA-256/size metadata
  and open one package-folder PR. Provider/contract changes need a separate
  infrastructure PR first; passing an old trusted validator is not possible until
  it supports the new contract. Do not lower the required Studio version to hide
  that dependency.

Older widget releases remain supported through Studio compatibility descriptors.
Clock, system monitor, drive and Bambu packages now ship their own descriptors.
Vivo Screen Sync keeps its existing app-owned Android settings API 1 unchanged.
Native `widgetApi: 1` / `studio-native-v1` and preset `pluginApi: 1` are unchanged;
new renderer kinds still require Studio support. Contract/provider changes require
maintainer review; changing native `studio` descriptors is not auto-merge eligible.

## GitHub checks and your required tests

Actions validate descriptor/defaults/ranges/choices, supported API/version, exact
source/embedded descriptor, receiver protection and all normal source/signature/
release checks. Errors and fixes appear on the PR. Settings contract changes
require maintainer review; new packages still need approval.

Test on physical Core and describe results/hardware/firmware in the PR: read
existing values; edit every field; apply/confirm; restart/persistence; upgrade
without data loss; rejection/timeout; install/launch/removal. State untested paths.
Static checks do not run app code or prove runtime behavior or source/binary
equivalence. An app that needs special trusted provisioning must document it.

## Printer model presets (Studio 0.50.0+)

The bambu-lan connection panel may additionally declare `model` as a `choice`
field with bounded `options` (`value` and `label`). Include `generic` as the
fallback. Accepted values are generic, a1, a1-mini, p1p, p1s, x1c, x1e, h2d,
h2s, h2c and h3c. This field requires minStudioVersion 0.50.0 or newer. Older
panels without model remain valid. The provider saves the selection on this PC
and sends its non-secret model identifier with telemetry. Existing connections
default to generic; widgets keep their printerId and placed layout. The model
selects presentation presets only, never firmware capabilities or commands.
