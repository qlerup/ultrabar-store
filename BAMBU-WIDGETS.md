# Bambu liquid widgets — Studio 0.46+

This contract adds a fixed trusted native renderer, `kind: "bambu"`, to
`widgetApi: 1` / `studio-native-v1`. It does not permit contributor runtime code,
scripts, arbitrary ContentProvider addresses or credential fields. This contract
requires the corresponding reviewed Studio 0.46 runtime before packages ship.

The companion `dk.ultrabar.bambu` APK owns the MQTT connection, credentials and
command authorization. Install/deploy the companion first, configure printers
there, then deploy the widget. The widget reads only its selected printer through
one fixed IPC endpoint, `content://dk.ultrabar.bambu.status`. The APK must restrict
IPC to its own UID, trusted root/ADB and the verified Core launcher system UID.
No credentials, serials, addresses or certificate pins are returned to the widget.

Normal widget id/name/background/textColor/accent fields still apply. Optional
printer fields (all are data):

| Field | Allowed values | Default |
| --- | --- | --- |
| primary | progress, state, remaining, temperature | progress |
| secondary | remaining, state, job, layers, temperature, none | remaining |
| expandedSlots | Integer 2, 3, 4 or 5 | 3 |
| showJob | Boolean | true |
| showTemperatures | Boolean | true |
| showLayers | Boolean | true |
| showRemaining | Boolean | true |
| showControls | Boolean | true |
| liquidMotion | Boolean | true |

Preferences belong to each placed widget. Tap expands across the selected number
of actual slots including their intervening gaps. Native neighbor views move left,
right or both depending on available space and source position. Corner radius
comes from the host card, and the settled outline uses Android's round rectangle.
The saved layout and scrolling order are unchanged. Collapse, outside tap or
Back restores every neighbor translation and original source opacity. Reduced motion follows the preference and Android's
animation setting. Information fades into the expanding shape; controls cannot
receive taps during the transition. Unknown/stale values are not shown as live.

Showing controls does not authorize printer commands. The companion must separately
enable controls, require fresh status, check the selected connection, validate the
fixed action whitelist, confirm stop and wait for printer telemetry rather than
interpreting MQTT delivery as success. No offline command replay is allowed.

Declare `compatibility.minStudioVersion: "0.46.0"` or higher and only physically
tested CB01/LineOS compatibility. Submit one **corebar-app package** with
`bundledWidgets` containing the full widget.json descriptor, identical to the
source root, submission and APK `assets/widget.json`. It uses one repository,
stable release, signed APK, Store listing, installation and update. Studio adds
the companion once to Background apps on widget placement and resolves the
matching APK on Deploy. Initial review and complete signature/source checks apply.

Required evidence: compact and 2/3/4/5-slot views, both screen edges, collapse,
outside tap, Back, rapid taps, reduced motion, stale/absent companion behavior,
per-widget editing/save/reload, and supported firmware. Record whether these
were tested with the actual LineOS host or only in the renderer preview harness.
Real printer acceptance remains separate from synthetic renderer/protocol tests.
