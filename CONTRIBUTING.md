# Publish or update an UltraBar Store package

**Detailed walkthrough:** [From your project to UltraBar Store](SUBMIT-A-PACKAGE.md).

## Package types and files

All types use `submissions/<package-name>/`. Declare the same `type` in repository.json and manifest.json: `corebar-widget` (integrated drag-and-deploy widget), `corebar-app` (standalone Android APK on Core), or `studio-plugin` (declarative presets, not executable PC plugins). New registrations require type; older approved registrations remain compatible.

Every package includes icon.png, README.md, LICENSE and the two manifests. Widgets include widget.json; presets include plugin.json (`pluginApi: 1`, a widgets list of name/kind/colors). APKs include app.apk and source.zip. APK upstream repositories contain AndroidManifest.xml at root, complete source and build instructions. Publish app.apk and a root-level git archive source.zip as stable release assets. The archive must exactly match every tracked file at the pinned commit (maximum 256 files/16 MiB, no symlinks/submodules).

APK Actions inspect package ID, versionName/versionCode, minimum SDK, exact permissions, non-debuggable status and a cryptographically verified v2 signature. APK updates preserve signing key and Android ID and increase versionCode. Binary/source equivalence is not automatically proven: source review and physical testing remain the maintainer's responsibility. SDK tools inspect data; submitted code is never executed.

The app receives a prebuilt APK at Install; it never compiles contributor source on the user's PC. Custom installation scripts are unsupported. Special provisioning must already be implemented by the app or by a trusted Studio version.


## Ownership model

Your widget lives in your own public GitHub repository. You choose collaborators and approve changes there. Forking your repository does not give someone permission to publish updates under your approved Store identity. The Store accepts submissions from the linked personal repository owner's GitHub account. Organization-owned repositories and ownership transfers require separate maintainer handling; they are not automatically approved.

Fork **qlerup/ultrabar-store** only to propose a listing or an update. You keep the source in your repository. New packages require owner review. Eligible existing-package updates receive bot approval and auto-merge after green checks; publishing a new upstream release alone does not update users.

## 1. Create your widget repository

Create your own public repository, or fork/copy an example you have permission to reuse. The root must contain:

```
widget.json
icon.png
README.md
LICENSE
```

Copy examples/clock/widget.json as a starting point. widgetApi is 1; runtime is studio-native-v1. Supported kinds: clock, cpu, memory, gpu, disk. Studio 0.24+ supports kindOptions containing two or three distinct cpu/memory/gpu values including the default kind. Each block then gets its own Show selector. Disk already has a per-block drive selector. Name/background/text/accent settings are supplied by Studio. The JSON is the complete source: arbitrary executable code and new renderer kinds are not supported by this format. Standalone APKs use the separate format above and require source/permission review.

icon.png must be static, square 256x256 or 512x512, maximum 256 KiB. Supply square artwork; Studio applies the rounded mask. Include redistribution rights for the icon and package in LICENSE. README describes settings, hardware, data collected, testing and limitations. Never include credentials or personal device identifiers.

Commit the files, then publish a stable GitHub release such as v1.0.0 pointing to that commit. Copy its full 40-character SHA. Do not move the tag or overwrite published assets after review.

## 2. Fork the Store list and submit a PR

Fork https://github.com/qlerup/ultrabar-store, create a branch and add a folder submissions/my-widget/. Include exact copies of the four root files from your release plus manifest.json and repository.json.

Copy this into repository.json and replace the values:

```json
{
  "repository": "YOURNAME/YOUR-WIDGET",
  "commit": "REPLACE_WITH_FULL_40_CHARACTER_COMMIT_SHA",
  "release": "v1.0.0",
  "type": "corebar-widget"
}
```

Copy examples/clock/manifest.json. Keep a stable unique package ID and stable widget IDs. Set source to https://github.com/YOURNAME/YOUR-WIDGET/blob/COMMIT_SHA/widget.json. Set version and actual compatibility. Native integration currently requires root-enabled ARM32 CB01, LineOS 1.0.8/1.0.9; PC hardware widgets need Studio connected. Reconnect after Core restart. Declare Studio 0.24.0+ for kindOptions.

Leave artifact/icon download metadata to the maintainer for first submissions. Never edit catalog.json. The maintainer publishes reviewed bytes as official versioned mirrors during review. This lets current Studio releases continue downloading through their verified official Store endpoint. The linked upstream repository remains the developer's source of truth; the mirror is a copy, not ownership of the project.

Open Contribute > Open pull request against qlerup/ultrabar-store main. GitHub inserts the copy/paste checklist from .github/pull_request_template.md automatically. Fill the links, version, changes and testing, and tick only completed items. Checkboxes are declarations; the Actions validate the actual data.

## 3. Automated checks and acceptance

The existing bot is deterministic GitHub Actions, not AI. Separate named steps test the validator, check package/schema/icon/compatibility, verify published bytes, and check repository ownership, update identity and upstream release files. Only trusted scripts from main run; contributor code is read as data, never executed.

For linked packages the PR author must match the repository owner. Updates keep the approved repository and package ID, increase version, and match exact upstream widget/icon/README/LICENSE bytes. A stable release must resolve to the reviewed commit. Repository redirects, archived/private repositories and unexpected ownership changes fail. Every changed submission, including first-party packages, requires repository.json. The initial migration of an approved legacy package is maintainer-only; subsequent updates are bound to the registered repository.

The comment lists checks and actionable errors. Push fixes to the same PR branch to rerun; maintainers can also use Actions > Store submission checks > Run workflow and enter the PR number. A green check and Ready for approval mean automated validation passed. New submissions require owner review of rights, functionality and physical testing. Eligible existing-package updates proceed to automatic approval and merge. The first review may report awaiting maintainer publication until official mirror metadata is prepared.

## Updates

1. Change files in your own widget repository and keep existing package/widget IDs.
2. Increase version, test and publish a new stable release at a new commit.
3. Create a new Store PR updating the same submission folder, repository.json commit/release, manifest/source/version and exact source copies.
4. The maintainer publishes new immutable mirrored files and prepares matching manifest metadata. Actions rerun all checks and verify your ownership against the approved listing.
5. After Store owner merge, users refresh the Store and see Update. No new Studio release is needed for supported capabilities.

Installed updates preserve existing placed blocks and settings. New defaults apply when adding a new block; Deploy sends the saved layout to Core. Removing a package removes its library template; remove placed blocks separately and Deploy. Existing drafts/backups remain available.

The repository owner can delegate development using GitHub collaborators, but under this initial policy only the owner submits Store releases. Support for organization teams or delegated publishers needs explicit maintainer approval. Owning a repository alone does not prove copyright; the maintainer also reviews rights.

## One package per PR

Each PR may change only one submission folder, including additions and removals. Submit separate PRs for separate plugins. In that folder, repository.json is the registration file: repository is YOUR_GITHUB_NAME/YOUR_REPOSITORY, commit is the full source SHA, release is the release tag, and type declares the package category. The bot checks this against the author and previously approved registration.

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
