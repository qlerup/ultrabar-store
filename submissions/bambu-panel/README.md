# Bambu Panel for UltraBar Studio

A local Bambu Lab printer integration for CoreBAR's ultrawide touchscreen, with
a companion app and the **Bambu Liquid** native home widget in **one Store package
and one installation**. Studio 0.46 lets each
placed widget choose its readings and unfold smoothly across 2, 3, 4 or 5 slots.
The companion owns the printer connection and credentials directly on CoreBAR.

The Studio 0.46 runtime and Store contract are under review. Released Studio 0.45
supports the companion app and its settings, but cannot render the new liquid
widget until the matching Studio update is installed.

![Native renderer preview with clearly labelled sample data](docs/preview.png)

![Expanded native renderer preview, sample data](docs/expanded.png)

[Watch the native unfold animation](docs/liquid-demo.mp4) (sample data, no printer connection).

## Install the widget

Install **Bambu Panel** once from Store after review. Drag its liquid widget onto
Core: Studio automatically adds the bundled app to **Background apps**, once even
with multiple placed widgets. Deploy with Studio 0.46+ installs the matching APK
and activates the widget together. App and widget share one source repository,
Store package and update. Open the app to configure printer profiles; select the printer to
monitor there. Multiple placed widgets can show different readings for that
selected printer.

In Studio choose **Main reading**, **Secondary reading**, unfolded size (2–5
slots), detail fields, controls visibility and liquid/reduced motion. Preferences
belong to each widget and follow the normal draft, Undo, Save and Deploy workflow.
The editor preview uses sample data, never pretends to read a real printer.

Tap the compact widget to unfold; tap outside, × or Back to collapse. The layer
grows from the actual card position and clamps at the visible screen edges. It
pushes neighboring cards left and/or right according to its position and chosen
size, without changing saved profile positions. Width includes the actual gaps
between slots, and the settled shape uses the host card's own corner radius.
Controls cannot be tapped during the transition. The spring/edge-wave animation
runs natively on Core; reduced motion also respects Android's animation setting.
Studio must reconnect to restore native cards after Core/LineOS restarts, just as
with Studio's other native widgets.

## Features

- Saved, separately encrypted connection profiles for up to 16 printers; switch
  with **Printers**. Only the selected printer is connected.
- Live job name, progress, remaining time and layer count.
- Legacy nozzle/bed temperatures and newer packed bed, chamber and extruder
  temperatures. Two-nozzle reports show both tool IDs; larger reports show the
  active tool. Values are displayed only when reported, never inferred by model.
- Pause, resume, stop with confirmation, and chamber light when reported.
- Controls default off. Stale status, disconnects and firmware that reports
  signed-command enforcement disable controls. No offline command replay.
- The app's **Preview** uses sample data and never sends printer commands.
- Studio settings API 1 for display name, controls, temperature visibility and
  keeping the screen awake. Connection credentials are entered only in the app.

This is an independent community project, unaffiliated with Bambu Lab or the
UltraBARX manufacturer. The name identifies compatible equipment. The original
printer icon and application source are MIT licensed.

## Printer compatibility

The connection is model independent: no serial-prefix or model allowlist. It
targets Bambu Lab printers exposing the local TLS MQTT status/control protocol,
including A1/A1 mini, P1, P2, X1/X2, H2 and H3 families. Availability depends on
each printer's actual firmware, LAN access and reported capabilities. This is
**not a claim that every model or firmware has been physically tested**.

Older single-nozzle and newer multi-extruder telemetry are covered by synthetic
tests. H2D and H3C are the owner's intended first printer tests; neither has yet
been tested with this release. CoreBAR install, launch and settings were tested
on CB01 / Android 10 / LineOS 1.0.9. Other Core firmware is not declared tested.

The first version handles common printing controls. Camera streaming, file
uploads, starting jobs, heater changes, AMS operations, tool-rack changes,
laser/cutting controls and cloud login are not implemented. Chamber light is
available only when `lights_report` includes `chamber_light`; absence does not
mean a printer has no light, only that this integration cannot safely control it.

## Connect a printer

1. Connect CoreBAR and printer to the same trusted LAN. Find the printer's IP,
   serial number and 8-character LAN access code in its network/device settings.
   **Search local network** listens for Bambu announcements for up to 8 seconds
   and fills IP, serial and name after selection. The access code is entered by
   you. Discovery results still require explicit certificate approval.
2. Enable the printer's LAN access. Recent firmware may require **LAN Only +
   Developer Mode** for third-party control. Follow your printer's manual; LAN
   Only can disable Bambu Handy/cloud functionality. Do not change modes while
   printing. This app does not change firmware or bypass signed authorization.
3. Open **Printers → Add printer**. Set a connection label, private IPv4 address,
   serial and access code. Choose **Save & connect**.
4. The app probes the TLS certificate **without sending credentials**. Compare
   its SHA-256 fingerprint with a trusted connection to that printer, then choose
   **Trust & connect**. First-use trust is not independent identity verification
   on a hostile network. Later connections require the exact approved certificate.
5. Confirm that live status matches the physical printer. Only then enable
   controls in Settings or Studio. Stop requires an additional confirmation.

**Settings → Save display** changes display/control preferences without modifying
the connection. To edit a saved connection, select it first, then open Settings.
Blank access code keeps the saved code only for the same address and serial.
Adding a profile with an existing serial updates that printer's saved profile.
Changing its address requires a new certificate approval. For a changed
certificate at the same address, forget that profile and add it again after
independently verifying the change. **Forget connection** removes only the selected
profile. Removing the final profile also deletes its Keystore encryption key.

Reconnect is explicit after a failure. Status is requested at connection and
every 15 seconds; printer state older than 30 seconds disables printing actions.
A sent command remains pending until subsequent printer telemetry confirms its
state, or times out after 12 seconds. MQTT acknowledgement alone is not success.
A timeout/disconnect can occur after the printer acted: check its physical state
before retrying. Commands are never automatically repeated.

The app and widget share one selected-printer connection through a foreground
service, with an ongoing Android notification. Visible widgets and the open app
renew a lease; the service disconnects within about 25–30 seconds without a
consumer. There is no boot receiver, wake lock or invisible permanent poller.
Keep screen awake applies only while the app is open. Connection failures still
require an explicit Reconnect; the service never replays printer commands.

## Privacy and permissions

Android permissions are `android.permission.INTERNET`, for the selected printer
at its private IPv4 address, TCP 8883 using TLS, and
`android.permission.FOREGROUND_SERVICE`, for the shared widget connection. No account, cloud service,
advertising, analytics, address-range scanning or runtime downloads are used.
Explicit discovery sends Bambu SSDP queries to multicast/broadcast UDP 1990/2021,
listens briefly, then closes its sockets. It never guesses passwords or saves
discovered devices until you save a selected profile. No camera,
storage, location or microphone permission is required.

Addresses, serials, codes and certificate pins are AES-GCM encrypted using an
Android Keystore key in app-private preferences; Android backups are disabled.
The root-enabled Core platform can access app data; encryption does not protect
against a compromised device. Display settings persist in separate app-private
preferences and contain no secrets. Live telemetry is memory-only. Clearing app
data or uninstalling removes app settings and saved profiles. An APK update with
the same signing key preserves them. Removing the Store library entry alone does
not uninstall the APK or erase app-private data.

One fixed ContentProvider gives the trusted Core launcher sanitised readings and
whitelisted controls. Only this app's UID, root/ADB, and UID 1000 verified against
the system Core launcher are accepted; ordinary Android apps are rejected. It
returns no printer addresses, serials, access codes, certificate pins or raw
printer reports. It checks the current selected connection again before sending
a command, so switching or forgetting a profile cannot control an old connection.

Studio settings require Studio **0.45.0+**, root-enabled CB01 ADB and settings API 1.
The descriptor is identical in source, Store manifest and APK assets. Its exported
receiver requires sender permission `android.permission.DUMP`; the app itself does
not request DUMP. Read/apply requests validate all fields, persist durably and
confirm actual saved values with the request revision. These app settings need
no custom provisioning scripts or credential fields. The separate native liquid
widget requires the reviewed Studio 0.46 renderer and fixed IPC implementation.

## Build

Requires Python 3.12, JDK 17/21, Android platform 35 and build tools 35.0.0. Build
the signed APK before creating a release. The app has **no third-party runtime
dependency** and uses Java/Dex only, compatible with ARM32 CB01 / Android API 29.
Its minimum SDK is 26, target SDK 29 and package ID is `dk.ultrabar.bambu`.

Set these environment variables to absolute paths / a private password:

```
ANDROID_BUILD_TOOLS=<sdk>/build-tools/35.0.0
ANDROID_PLATFORM_JAR=<sdk>/platforms/android-35/android.jar
ANDROID_KEYSTORE=<private-directory>/bambu-panel-release.jks
ANDROID_KEY_PASSWORD=<private-keystore-password>
```

Create a private release key once with `keytool -genkeypair` (RSA 3072 or stronger),
then run `python build.py`. Output: `dist/app.apk`. Retain the private key and
password securely for updates; neither belongs in Git or a release archive.
CI uses a disposable signing key and never publishes that test APK as a release.

```
python -m pip install -r requirements-test.txt
python test.py
```

Tests checksum-verify the test-only JSON jar. The fake MQTT printer binds the
test machine's private IPv4 on port 8883, using an ephemeral test TLS certificate.
Set `BAMBU_TEST_ADDRESS` if automatic local-interface selection is unsuitable.
It never connects to a real printer. Use `python tools/test_device.py --adb PATH
--serial DEVICE` for the physical settings smoke test; it requires root-enabled
ADB, restores display settings and leaves the app stopped.

Regenerate the included original icon with `python tools/make_icon.py` (Pillow).
For Store source, use `git archive --format=zip --output=dist/source.zip COMMIT`:
all tracked files at archive root, no private keys, binaries or local test outputs.
Publish immutable `app.apk` and `source.zip` stable release assets. Store submission
files and checks are described in [the release checklist](docs/STORE-REVIEW.md).

## Sources and protocol limits

- [UltraBar Store contribution requirements](https://github.com/qlerup/ultrabar-store/blob/main/CONTRIBUTING.md)
- [Studio settings API 1](https://github.com/qlerup/ultrabar-store/blob/main/APP-SETTINGS.md)
- [Bambu Lab: third-party integration and Developer Mode](https://blog.bambulab.com/updates-and-third-party-integration-with-bambu-connect/)
- [Bambu Lab H2D manual](https://csm.bblcdn.com/hub/4668d0ca43994ff3bff4b37f1a65c2e7.pdf)
- [Bambu Studio source](https://github.com/bambulab/BambuStudio)
- [ha-bambulab telemetry implementation](https://github.com/greghesp/ha-bambulab/blob/main/custom_components/bambu_lab/pybambu/models.py)
- [Hardware-observed MQTT notes](https://github.com/voska/bambu/blob/main/docs/protocol.md)
- [Bambu Bar — visual reference](https://github.com/rolottr/bambu-bar)

The local MQTT protocol is not an officially supported Bambu Lab public API.
Packet and field handling here is independently implemented; external projects
were consulted for protocol facts, not included as application dependencies.
`StudioSettingsBridge.java` is copied from the Store's MIT example; its copyright
notice is retained in LICENSE. Firmware changes may require an app update.
