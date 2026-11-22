# From your project to UltraBar Store: step-by-step guide

**Before building:** read [APP-SETTINGS.md](APP-SETTINGS.md) for the exact Studio
integration requirements and [complete example](examples/settings-app). Android
apps with editable Studio settings require settings API 1 and Studio 0.45+;
native widgets can own their controls through widgets[].studio (Studio 0.49+),
using the approved runtime/providers documented there.

Your project lives in **your own public GitHub repository**. Fork
`qlerup/ultrabar-store` to propose a listing or update. You control your source
repository and its collaborators; the Store owner approves each Store release.
Another person's fork cannot publish updates under your approved package identity.

## 1. Choose the package type

| Type | What users receive | Package file |
| --- | --- | --- |
| `corebar-app` | Standalone Android app installed and run on Core | Prebuilt, signed `app.apk` |
| `corebar-widget` | Widget in the left library, dragged onto the bar, configured on the right and activated with Deploy | `widget.json` |
| `studio-plugin` | Settings/presets for existing widget types | `plugin.json` |

Vivo Screen Sync is a **corebar-app** because it runs a background service on Core.
Clock & Date, Drive Usage and System Monitor are **corebar-widget** packages.
A widget package can offer multiple choices; each placed block has its own settings.
The preset format supports declarative settings only, without executable PC plugins.

For a standalone Core app, implement the app's setup, storage and runtime in its
own APK. Provide an exported Android launcher activity. Use the optional
[Studio settings API](APP-SETTINGS.md) for settings that benefit from being
edited on the PC. Keep credentials and device-specific setup in the app.
Studio 0.52.15 and later can install a staged standalone app with **Install on
Core**, including an app added from a local folder. This installation leaves
the Core layout alone. Open the app on Core after installation.

All types use `submissions/<unique-package-folder>/`. Declare the same **type** in
`repository.json` and `manifest.json`; Actions rejects mismatches. Each PR may
change only one package folder. Separate types do not need separate folder trees.

## 2. Create your own repository

1. Sign in to GitHub with the personal account that will own the package.
2. Choose **New repository**, enter a name and select **Public**.
3. Add complete source, `README.md`, `LICENSE` and `icon.png`.
4. Supply a square, static PNG icon at 256x256 or 512x512, at most 256 KiB.
   Studio applies rounded corners consistently to every icon.
5. Explain functionality, setup, permissions, data use, requirements, tests and
   limitations in README. LICENSE must permit your intended Store distribution.
   Keep keys, tokens and personal device information out of Git.

For **widgets**, put `widget.json` at repository root. Start with
`examples/clock/widget.json`. Supported kinds are clock, cpu, memory, gpu and disk.
`kindOptions` enables per-block CPU/RAM/GPU selection and requires Studio 0.24+.
Disk widgets have a per-block drive selector. New renderers and executable code
require a different supported integration; JSON cannot introduce them.

### Implement settings inside your package

For a native widget, add an optional **`widgets[].studio`** object directly to the
root `widget.json`; do not add Android `settings` to the package manifest. This
complete example exposes seconds/date/time format through Studio's shared editor:

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

Set `manifest.json` -> `compatibility.minStudioVersion` to **`0.49.0`** (or newer)
and keep `hostApi: 1`, `permissions: []`, stable package/widget IDs and the tested
CB01/ARM32/LineOS matrix. The package owns field labels/options/defaults/help;
Studio owns rendering, validation and per-widget draft/Undo/Save/Deploy. Existing
saved values override package defaults. Keep keys and runtime defaults compatible.

The [native panel implementation guide](APP-SETTINGS.md#native-widget-panels-studio-049)
provides the exact supported keys/types per renderer, a complete live Drive source
example, a complete Bambu connection form/provider example, certificate approval
requirements, settings scopes, developer checklist and executable validation commands.
Use `sources: {"drive":"pc.drives"}` only for the supported disk setting. Use
`connection.provider: "bambu-lan"` only with its documented exact fields and
`printerId` selection key. Unsupported providers/fields are rejected; the package
cannot supply JavaScript, commands or arbitrary networking code. A new protocol
requires a reviewed trusted Studio provider implementation before package use.

For an Android app, continue using **settings API 1**: include root and embedded
`studio-settings.json`, implement the protected fixed `.StudioSettingsReceiver`,
validate read/apply requests and return confirmed saved values. Those values are
global to the Android app, unlike native per-widget settings. Follow the complete
[Android implementation contract](APP-SETTINGS.md#mandatory-files-and-android-component)
and [buildable receiver example](examples/settings-app). Vivo Screen Sync already
uses this route and does not require migration to native widget panels.

Before releasing, run the validation commands/checklist in that guide and verify
installation, editing, save/reload, update without data loss and physical Deploy.
Describe untested hardware paths honestly. Schema/provider support changes belong
in a separate Store infrastructure PR before your one-package submission PR.

For **presets**, put `plugin.json` at repository root:

```json
{
  "pluginApi": 1,
  "widgets": [{"name": "My RAM preset", "kind": "memory", "accent": "#A5DFCB"}]
}
```

For **Android apps**, put `AndroidManifest.xml` at repository root and include
complete source and build instructions. Build a release APK with
`debuggable=false`, minimum Android API 26 and an APK v2 signature. Keep your
private signing key for future updates. Choose a unique Android package ID outside
reserved system and UltraBar namespaces. Special setup must already be supported
by Studio or handled by the app; manifests cannot add install scripts.

## 3. Test and publish an upstream release

1. Test on the hardware and firmware you intend to support.
2. Choose a version such as `1.0.0` and commit all source files.
3. Record the full 40-character commit SHA for your registration.
4. Open **Releases > Draft a new release**, create tag `v1.0.0` at that commit
   and publish a stable release, rather than a draft or prerelease.
5. Widgets and presets already have their package JSON in the pinned source.
   Android apps also require **app.apk** and **source.zip** as release assets.
   Create the archive with `git archive --format=zip --output=source.zip HEAD`.
   It must contain exactly all tracked files at archive root, without an extra
   enclosing directory: at most 256 files/16 MiB uncompressed, no submodules or symlinks.
6. Keep published tags and assets immutable. Publish a new release for corrections.

When a user selects Install, Store downloads the **prebuilt APK**. You can build
releases with GitHub Actions in your own repository; keep signing keys in private
secrets. Compilation does not run on the user's PC during installation.

## 4. Fork Store and create one package folder

1. Open https://github.com/qlerup/ultrabar-store and select **Fork**.
2. Create a branch in your fork, such as `submit/my-app`.
3. Create `submissions/my-app/`.
4. Copy exact release files, preserving their bytes and line endings:

```text
submissions/my-app/
  repository.json
  manifest.json
  icon.png
  README.md
  LICENSE
  widget.json       # corebar-widget only
  plugin.json       # studio-plugin only
  app.apk           # corebar-app only
  source.zip        # corebar-app only
```

Include only the files for your selected type. For APKs, Actions compares
source.zip with the pinned upstream Git tree. Both app.apk and source.zip must
also exactly match the assets published on your own release.

## 5. Complete repository.json

Copy this and replace the example values:

```json
{
  "repository": "YOUR_GITHUB_NAME/YOUR_REPOSITORY",
  "commit": "REPLACE_WITH_FULL_40_CHARACTER_COMMIT_SHA",
  "release": "v1.0.0",
  "type": "corebar-app"
}
```

`repository` contains your GitHub account and repository name, without a full URL.
The personal account opening the PR must own that repository. Organizations,
delegated publishers and ownership transfers require separate maintainer handling.

## 6. Complete manifest.json

Start with an example or approved package of the same type. Set:

- `schemaVersion`: 1; a stable unique `id`, name, description and version.
- `type`: exactly the value declared in repository.json.
- `publisher`: your GitHub account, matching the registered repository owner.
- `source`: `https://github.com/OWNER/REPO/blob/SHA/widget.json`, `plugin.json`
  or `AndroidManifest.xml`, depending on package type.
- `license`: a short description of the package license.
- `compatibility`: minimum Studio version, `hostApi: 1`, supported models,
  firmware versions and ABIs. Native widgets require the documented CB01/ARM32/LineOS
  integration. Report untested hardware explicitly.
- `permissions`: an empty list for JSON packages; exactly the Android permissions
  requested by the APK for Core apps.
- APK only: `android` with `packageId`, integer `versionCode`, `minSdk` and
  `signerSha256` from `apksigner verify --print-certs app.apk`.

A first submission may omit `artifact` and `icon` download metadata. During review,
the maintainer publishes the reviewed files as immutable assets in the official
Store repository and supplies the URL, byte size and SHA-256 in the package manifest. GitHub generates the catalog entry automatically after merge. Checks become fully green after this publication step.
The mirror distributes a reviewed copy; your repository remains the source's home.

## 7. Open a PR and complete the checklist

1. Commit the package folder in your fork.
2. Select **Contribute > Open pull request** against `qlerup/ultrabar-store:main`.
3. Complete the automatic template: package type and ID, your repository, release,
   commit, changes, test results and limitations.
4. Tick only completed items. Declarations do not replace automated validation.
5. Wait for **Store submission checks**. Submitted files are treated as data;
   Actions never runs your submitted code or workflow changes.

## 8. Fix errors and rerun checks

The bot updates its comment with checks performed and actionable errors. Fix the
files and push to the **same PR branch** to rerun Actions automatically. If a fix
changes upstream source or the build, first publish a new upstream release and
update the submitted SHA, tag and files. A maintainer can also open
**Actions > Store submission checks > Run workflow** and enter the PR number.
If two package folders changed, split them into separate PRs.

**Ready for approval** and green checks mean automated file, identity and package
validation passed. They do not prove security, copyright ownership or hardware
functionality. The Store owner reviews new packages and changes requiring manual approval; eligible existing-package updates can merge automatically after checks.

## 9. Approval and user installation

After the Store owner merges the PR, the listing is eligible for automatic catalog publication. Users
open Store and select **Refresh store**. GitHub caching can cause a short delay.
A new Studio release is unnecessary when the installed version already supports
the package's type, capabilities and declared minimum version.

- Core app: connect Core, select Install, then open it in Core's app list.
- Core widget: Install, find it in the left library, drag a block onto the bar,
  configure that block on the right, then Deploy.
- Preset: Install into the library, add a block and Deploy like a widget.

## 10. Submit an update

Keep the approved repository, package ID and type. Update the source in your
repository, increase the version, test, commit and publish a new stable release.
APKs must also increase versionCode and keep their Android package ID and signing
key. Open a new Store PR updating the **same package folder** with the new files,
SHA and release. Ownership verification and all checks run again. Eligible updates merge automatically; changes outside the automatic-update policy require owner approval. Users can fetch the update after merge.

Publishing an upstream release alone does not update Store. Another person's fork
cannot take over your approved registration. Android updates preserve app data;
the app developer is responsible for any data-format migration. Widget updates
preserve settings of blocks users have already placed.

## Uploader identity

Every manifest declares `publisher`, the GitHub account owning the registered repository. Actions verifies this against `repository.json`, source URL and PR author. Studio displays **Uploaded by @ACCOUNT** on the package card. Changing this field cannot transfer package ownership. All changed packages require repository.json; the former first-party registration exemption has been removed.

## Automatic merge for existing-package updates

A PR updating one already approved and registered package can merge automatically
after all required checks pass. The trusted Actions job approves the exact checked
commit and enables GitHub auto-merge. GitHub still requires green checks and an
up-to-date branch. The bot never runs submitted code.

Automatic approval requires the same registered repository, publishing account,
package ID/type, license, permissions and compatibility. Android updates must
also preserve package ID, signer and minimum SDK while increasing versionCode.
The package version must increase. Only that package folder may change. Changes to workflows, other packages or catalog.json
require manual approval. New packages, first repository-registration migrations,
identity changes and permission/requirement changes also require manual approval.
An outstanding changes-requested review prevents automatic approval. Add the
`store-manual-review` label before validation to keep an update manual.

The existing one-review requirement remains enabled. Only eligible updates receive
a bot approval; new submissions still require a maintainer review/merge. Review
results appear in the **Merge eligible package update** job. Publishing an upstream
release alone still does not create a Store PR or update users. Reviewed immutable
artifact/icon mirrors and matching package manifest metadata are still required for checks
to pass. Users install the package update through Studio's Store; Studio itself
does not need an update.

## Generated catalog: no shared-list edits in package PRs

Each package has one folder under submissions/. Its manifest.json is the source
for its Store card; repository.json records the source owner and release. Change
only that folder when submitting a package or update. Do not edit catalog.json.
GitHub validates a freshly generated catalog during PR checks, then publishes the
complete approved list on the data-only `catalog` branch after merge. Packages
are sorted by ID, and invalid or duplicate entries stop publication. Failures leave
the last successful published catalog intact. Separate package PRs therefore do
not compete over a shared JSON array.

Studio 0.31+ reads `catalog/catalog.json` from that generated branch. The old
main/catalog.json is a frozen compatibility snapshot for older Studio clients;
it is not the live list and must not be updated in package PRs. One Studio upgrade
is needed to switch to the new feed. Subsequent supported package releases do not
require Studio updates. Publication normally follows merge; a scheduled recovery
also checks every five minutes because bot merges can suppress ordinary push
workflows. Refresh Store after publication to see the new list.

## Request removal or restore a package

Package owners can open **Issues > New issue > Request package removal**, enter the
package ID and reason, and submit from the GitHub account owning the registered
repository. A deterministic Actions check verifies that account and comments on
the request. It does not remove the listing automatically.

The Store maintainer opens **Actions > Remove or restore package > Run workflow**,
selects main, enters package_id, chooses remove or restore, and supplies a public
reason. Optionally enable dry_run to preview without creating anything. A normal
run creates a listing-only PR and starts validation. Review and merge that PR to
publish the change. Listing changes never auto-merge. The workflow summary links
to the prepared PR.

The per-package listing.json records listed=false and a reason. Source files,
registration, release assets and existing user installations are retained. The
generated live catalog excludes the package after merge; installed copies can
still be managed locally. Restoration is a maintainer decision using the same
workflow with action=restore. Package owners may also propose listing.json=false
in their own package folder without changing the package version; the maintainer
still reviews the removal PR.

## Test before submitting

Studio 0.32+ can install a local package with **Install from folder**. See
https://github.com/qlerup/ultrabar-studio/blob/main/docs/LOCAL-PACKAGE-TESTING.md .
Local development packages are explicitly marked and are not published to Store.


## Widget sizes

A `studio-native-v1` widget descriptor may declare `"sizes": ["large", "small"]`
on an individual entry in `widgets`. Use `["large"]` or `["small"]` to limit
that widget to one size. Studio picks the matching native presentation and
offers only the supported sizes. New widgets default to large when supported.
When the field is omitted, both sizes are available in Studio 0.52.0 and later.

Set `compatibility.minStudioVersion` to at least `0.52.0` when declaring sizes.
For a small-only package, list only LineOS `1.0.9` in
`compatibility.lineosVersions`. Mixed layouts require root-enabled CB01 with
LineOS 1.0.9. Verify readability in both sizes you declare before submitting.

## Package-defined settings in Studio 0.52.18

A widget installed in Studio can set `widgets[].studio.api` to `2`. Declare the
editor controls in `studio.settings.fields`. Each field supplies its own key,
label, type and default. The same Studio version reads added fields, choices
and defaults when the package is updated. Values belong to each placed card.
Use a stable package ID, widget ID and field key across releases.

For example, a package can declare a color as
`{"key":"plate","label":"Plate color","type":"color","default":"#353839"}`
and set `plateColorSetting` to `plate` in its split-flap presentation preset.
A choice field can select a package-defined presentation through
`presentation.source`. A printer presentation preset can specify
`minTemperatureRows` from 1 to 3. The existing Core layout applies these values
on Deploy. Publish changes to the widget JSON through the existing Store listing.

Supported field types are boolean, integer, number, string, URL, choice and
color. New field keys are stored under `packageSettings`, separately from the
card identity and transport settings. A field supplies configuration. A feature
that uses it also needs a renderer, presentation or device capability that
consumes its value. Declare `compatibility.minStudioVersion` of at least
`0.52.18` for panel API 2.

### Shared widget layouts

Panel API 2 accepts a `layout` object with a `large` and a `small` array. Each array declares up to 32 layers drawn in order. Use coordinates on a 260 by 240 canvas for large cards and 130 by 120 for small cards. Each layer declares an `op` and a `box` containing x, y, width and height. Supported operations are text, rect, bar, image and time. Bind a color to a field with `$fieldName`, text to a value with `@fieldName`, and visibility with `when`. For example, `{"op":"rect","box":[4,4,50,20],"color":"$plateColor"}` draws a plate in the selected color. Time layers continue ticking locally on Core. Studio previews the installed layout and Deploy supplies the same graphics to the home card. Keep the widget ID stable when changing layouts.

For printer presets with at least two temperature rows, Studio 0.52.21 supports an optional `nozzleGrid` with integer pixel dimensions. Set `materialSize` (10 to 20), `swatchSize` (8 to 22) and `verticalInset` (4 to 14). Reducing the vertical inset leaves more height for the tiles.
