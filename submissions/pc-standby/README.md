# PC Standby for UltraBar Core

PC Standby follows the Windows copy of UltraBar Studio that deployed it. Core
asks Studio for an authenticated reply once every 30 seconds. After three
consecutive unanswered pings, Core goes to sleep. A valid reply resets the count.
If a touch wakes the screen while Studio is still unreachable, Core goes back to sleep.
When Studio answers again, PC Standby wakes Core if it put the screen to sleep.

## Install

Requires UltraBar Studio 0.52.26 or newer and CB01 with root-enabled WiFi ADB
and LineOS 1.0.9.

1. In the Studio Store, install or update **PC Standby**.
2. Drag it to **Background apps** or onto the Core bar in the layout preview.
3. Choose **Deploy to Core**. Studio installs the APK, grants the two device
   permissions it needs, pairs Core and verifies that Core received a reply.
   No separate Windows helper, pairing code or Android setup is needed.
4. To turn monitoring off, remove PC Standby from the layout and background
   apps and deploy again. Studio restores Core's previous inactivity timeout.

Closing the Studio window to the system tray keeps Studio available. Exiting
Studio entirely, suspending or shutting down the PC, and a sustained loss of
WiFi ADB all stop replies. The first missed ping may be up to 30 seconds after
disconnection. The two additional checks take another 60 seconds. Studio
restores its connection when it starts again. The settings in Studio include a
**Start with Windows** option for automatic startup after sign-in.

The app on Core shows connection status. If you want to uninstall the APK from
Android, first remove it from the Studio layout and deploy. Then open the app
and select **Remove sleep permission** before uninstalling.

## Permissions and data

- `INTERNET` allows Core to query the Studio presence endpoint on its own loopback.
- `FOREGROUND_SERVICE` runs visible background monitoring on Core.
- `RECEIVE_BOOT_COMPLETED` resumes enabled monitoring at Core boot.
- `WRITE_SETTINGS` lets the app change and restore the inactivity timeout.
- `WAKE_LOCK` keeps the monitor able to detect when Studio returns.
- The device admin receiver uses only force-lock to put the display to sleep.
  Studio provisions this permission through the already authorized root ADB link.

Studio binds the presence endpoint on Windows loopback. Core reaches it via an
ADB reverse tunnel. The endpoint only signs a challenge for a paired Core and
serves no Studio data or control commands. Pairing keys stay in Studio's local
data folder and Android app-private storage. The app uses no cloud service or
analytics. On activation it sets the LineOS timeout to Never and records the
previous value for restoration. Normal Android screen-lock rules still apply.

Existing 1.0.0 manual pairings are preserved until the first Studio Deploy.
If you installed the separate Windows companion for 1.0.0, that companion is
no longer required after Deploy. Its original script can remove its scheduled
task and firewall rule with the `-Remove` option.

## Build

Set `ANDROID_BUILD_TOOLS` to Android build-tools 35.0.0,
`ANDROID_PLATFORM_JAR` to platform 35's android.jar,
`PC_STANDBY_KEYSTORE` to a private signing keystore and
`PC_STANDBY_KEY_PASSWORD` privately. With Python 3 and JDK 17+, run
`python build.py` to produce and verify `app.apk`.

```text
javac -d build/tests src/dk/qlerup/corestandby/Presence.java tests/dk/qlerup/corestandby/PresenceTest.java
java -cp build/tests dk.qlerup.corestandby.PresenceTest
```

Create the exact Store source snapshot with
`git archive --format=zip --output=source.zip HEAD`. The original launcher
artwork is in `res/drawable/ic_launcher.xml`. Run `python make_icon.py` with
Pillow to regenerate the Store PNG.
