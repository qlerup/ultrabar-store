# PC Standby for UltraBar Core

PC Standby replaces Core's inactivity timeout with a connection check to a paired
Windows PC. Core sends a new local-network ping about every five seconds. A valid
reply keeps the screen on even if nobody touches Core. After the PC has answered
at least once, about 20–26 seconds without an answer puts Core to sleep. A new reply
wakes Core if the app put it to sleep during the current monitoring session.

Shutting down or suspending the PC stops replies. The same happens if Windows
stops the companion or the local network goes down. Short interruptions are
filtered out. If Core starts before the PC ever replies, the app waits for the first
answer before issuing any sleep action. The original timeout applies until the
first successful connection on a new installation.

## Setup

Supported hardware: UltraBar Core CB01 (ARM32), LineOS 1.0.9, with a Windows PC
on the same trusted private IPv4 network. Install the Core app through UltraBar
Studio 0.45.0 or newer. In Studio, add PC Standby to the Core layout or
**Background apps**, then choose **Deploy to Core**. Open the app on Core to
configure it. There are no Studio settings fields.

1. Download and extract `windows-companion.zip` from the latest [PC Standby release](https://github.com/qlerup/ultrabar-core-standby/releases/latest).
2. Find Core's IPv4 address in UltraBar Studio, then open Windows PowerShell as
   Administrator in the extracted folder. If Windows marks the script as a download,
   review it and then run `Unblock-File .\PC-Standby.ps1`. Run setup with your
   Core's address, for example `.\PC-Standby.ps1 -CoreAddress 192.168.0.50`.
   Setup prints the PC's IPv4 address and its 32-character pairing code.
3. On Core, open **PC Standby** and grant **Allow changes to screen timeout** and
   **Allow PC Standby to put Core to sleep**. Enter the Windows IPv4 address and
   pairing code, then select **Start monitoring**.
4. Verify the Core notification says **Paired PC connected**. If either device
   changes IPv4 address, rerun the Windows setup for the new Core address and
   update the PC address in the Core app. DHCP reservations can keep both stable.

Windows setup creates one startup task, **UltraBar PC Standby**, and a Private
network inbound rule for UDP port 47431 limited to Core's IPv4 address. The task
keeps running when Studio is closed and Windows is at the sign-in screen. The
companion answers an HMAC challenge with a dedicated pairing key. It handles
only fixed-size ping packets and cannot control the PC. Core stores the pairing
code privately, and Windows stores the key under Program Files. No cloud
connection or telemetry is used.

## Pause or remove

On Core, select **Pause monitoring** before removing the app. It restores the
previous inactivity timeout if the setting still belongs to PC Standby. Then
select **Remove sleep permission**, then uninstall the app.
If the app was force-stopped or removed before pausing, set the desired timeout
in the Core display settings. Android screen-lock rules, including a PIN if one
is set, still apply after wake. Tap Core to wake it manually while the PC is away.

On Windows, run `.\PC-Standby.ps1 -Remove` as Administrator to remove the
startup task, firewall rule, installed script and pairing key.

## Permissions

- `INTERNET` for local UDP pings.
- `FOREGROUND_SERVICE` for visible connection status and background monitoring.
- `RECEIVE_BOOT_COMPLETED` to resume enabled monitoring after a Core reboot.
- `WRITE_SETTINGS` (user granted) to save, replace and restore Core's timeout.
- `WAKE_LOCK` to let the service monitor reconnection while the display is asleep.
- Device admin (user granted) uses only the force-lock policy to put Core to sleep.

The app uses **Never**, the LineOS timeout setting, while monitoring an
authenticated PC. The foreground service holds a CPU wake lock while enabled
so that it can detect the PC's return with the screen off.

## Build and test

Set `ANDROID_BUILD_TOOLS` to Android build-tools 35.0.0,
`ANDROID_PLATFORM_JAR` to platform 35's android.jar,
`PC_STANDBY_KEYSTORE` to a private signing keystore, and
`PC_STANDBY_KEY_PASSWORD` privately. With Python 3 and JDK 17+, run
`python build.py` to produce and verify `app.apk`.

Run the Java connection timing test with:

```text
javac -d build/tests src/dk/qlerup/corestandby/Presence.java tests/dk/qlerup/corestandby/PresenceTest.java
java -cp build/tests dk.qlerup.corestandby.PresenceTest
```

Use `git archive --format=zip --output=source.zip HEAD` for the complete Store
source snapshot. The Windows zip contains the tracked `windows/PC-Standby.ps1`
at its root. The original launcher artwork is in `res/drawable/ic_launcher.xml`.
Run `python make_icon.py` with Pillow to regenerate the Store icon.

## Verification for 1.0.0

On a physical CB01 with LineOS 1.0.9 and the Windows responder running on the
same LAN, a valid reply selected the Never timeout. A brief interruption left
the display on. Stopping the responder made Core report display OFF, and
restarting it woke the display. Pausing restored the original five-minute
timeout. Removing the sleep permission allowed normal Android uninstall.
The Windows responder protocol, Java timing tests and signed APK were also
verified. The Windows startup-task and firewall installation, reboot and
installation from the published Store listing were not exercised.
