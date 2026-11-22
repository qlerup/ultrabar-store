# Flip Clock HD

Flip Clock HD is a full-screen animated LineOS screensaver for UltraBar Core.
The digits sit directly on the flaps in each photographed scene, and the
photographed plates fold at the hinge when the time changes.

## Install and configure

Requires UltraBar Studio 0.52.29 or newer and Core CB01 with root-enabled
WiFi ADB and LineOS 1.0.9.

1. Install **Flip Clock HD** in the Studio Store. Add it to **Background apps**
   or the Core bar in the layout preview.
2. Select Flip Clock HD in the editor to change the theme, date, seconds or
   idle delay. Supported delays are 20, 40, 60, 80 and 100 seconds.
3. Select **Deploy to Core**. Studio installs the app, applies its settings,
   and selects Flip Clock HD in place of the previous LineOS screensaver.
4. Tap Core while the clock is showing to dismiss it. Launching the app
   directly on Core also opens the full-screen clock.
Keep Studio connected, including in the Windows tray, so it can re-arm the
LineOS 1.0.9 idle timer when the clock is dismissed.

5. To restore the previous screensaver, remove Flip Clock HD from the layout
   and Background apps and deploy again.

LineOS triggers the screensaver while the display is awake. PC Standby can
still turn the display off. Flip Clock HD does not change Android's screen-off
timeout or PC Standby's connection checks.

## Themes

- **Graphite** has charcoal plates, a warm edge highlight and walnut trim.
- **Ivory** uses cream plates, a pale shell and a textured linen surround.
- **Midnight** uses blue metal and cool edge lighting.

Each theme comes with matching four-flap and six-flap versions. Showing
seconds uses the six-flap photograph. The clock follows Core's time, locale
and 12/24-hour setting. Artwork and generation prompts are in [ARTWORK.md](ARTWORK.md).

## Settings and data

The app declares no requested Android permissions and uses no network or
analytics. It stores the display choices in app-private preferences. Settings
API 1 uses an Android broadcast receiver protected by `android.permission.DUMP`
and requires Studio to confirm the values saved on Core. All visual settings
are edited in Studio. The Core clock itself shows no settings controls.

## Build

With JDK 17+, Python 3 and Android build-tools/platform 35, set
`ANDROID_BUILD_TOOLS`, `ANDROID_PLATFORM_JAR`, `FLIP_CLOCK_KEYSTORE` and
`FLIP_CLOCK_KEY_PASSWORD`, then run `python build.py`. The build signs and
verifies `app.apk`. Keep the keystore private for future updates.

The exact Store source archive is produced by
`git archive --format=zip --output=source.zip HEAD`.
