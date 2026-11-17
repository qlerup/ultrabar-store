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

```json
{
 "widgetApi":1,"runtime":"studio-native-v1",
 "widgets":[{"id":"clock","name":"Clock","kind":"clock",
  "studio":{"api":1,"settings":{"api":1,"fields":[
   {"key":"showSeconds","label":"Show seconds","type":"boolean","default":true}
  ]},"help":"Uses Core time and locale."}}]
}
```

Declare `compatibility.minStudioVersion` **0.49.0 or later**. See
[widget-studio.schema.json](widget-studio.schema.json); the trusted
`scripts/widget_studio_contract.py` checks renderer-specific supported fields,
types and choices. Descriptors are at most 32 KiB, plain text only. Settings use
the field types and bounds above; authors should align declared defaults with
the widget runtime defaults. Existing saved values override defaults. Stable keys and widget
IDs preserve placed cards. Studio continues to supply common names/colors.

Supported settings: clock `hourFormat`, `showSeconds`, `showDate`; system monitor
`kind` (CPU/RAM/GPU); disk `drive`; Bambu `primary`, `secondary`, `expandedSlots`
(integer 2-5), `showJob`, `showTemperatures`, `showLayers`, `showRemaining`,
`showControls`, `liquidMotion`. Choices cannot introduce unsupported runtime
behavior. A disk panel may use `sources: {"drive":"pc.drives"}` with a string
`drive` setting (maxLength 128, default `all`); Studio offers All drives, current
PC drives and the saved value. This approved data source is not a URL or script.

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
