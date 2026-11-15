# Studio settings API 1 example

See [APP-SETTINGS.md](../../APP-SETTINGS.md) for all integration requirements.
This app demonstrates six field types and reads, validates, durably saves and
confirms actual settings. Copy the directory to your own repository; change the
package name and implement real read/apply hooks. Add your Store manifest,
registration and icon as described in the guide. Never commit signing keys.

Build with JDK and Android SDK tools. Set ANDROID_BUILD_TOOLS to the directory
containing aapt, zipalign and lib/apksigner.jar; ANDROID_PLATFORM_JAR to android.jar;
ANDROID_KEYSTORE and ANDROID_KEY_PASSWORD to your private signing configuration.
Run `python build.py` to produce app.apk with the embedded descriptor. Submit
your own stable release and pinned source.zip. This example is not a Store listing.
