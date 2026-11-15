# From your project to UltraBar Store: step-by-step guide

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
Store repository and supplies the URL, byte size and SHA-256 with an identical
catalog entry. Checks become fully green after this publication step.
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

After the Store owner merges the PR, the listing is in the main catalog. Users
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
The package version must increase. Only that package folder and its exact catalog
entry may change. Changes to workflows, other packages or unrelated catalog entries
require manual approval. New packages, first repository-registration migrations,
identity changes and permission/requirement changes also require manual approval.
An outstanding changes-requested review prevents automatic approval. Add the
`store-manual-review` label before validation to keep an update manual.

The existing one-review requirement remains enabled. Only eligible updates receive
a bot approval; new submissions still require a maintainer review/merge. Review
results appear in the **Merge eligible package update** job. Publishing an upstream
release alone still does not create a Store PR or update users. Reviewed immutable
artifact/icon mirrors and matching catalog metadata are still required for checks
to pass. Users install the package update through Studio's Store; Studio itself
does not need an update.
