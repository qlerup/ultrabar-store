# Submit a widget to the UltraBar Store

A submission is a GitHub pull request, not a direct upload into the live store.
Only the owner, qlerup, publishes approved entries. A green automated check is
not approval and does not install or publish anything.

## What can I submit today?

Studio 0.20 supports integrated `corebar-widget` packages. One package installs
into the Studio library; the user drags its widget onto the bar, edits the right
panel and presses Deploy. Studio sends the renderer and settings to Core.
You do not submit a separate PC program or APK for these widgets.

The `studio-native-v1` runtime supports `clock`, `cpu`, `memory`, `gpu` and `disk`.
It supplies the editor controls, data collection and Core rendering. Clock
options are 12/24 hours, seconds and date; disk has a drive selector. All have
name/background/text/accent controls. Core clock time/locale may differ from the
PC preview. Hardware metrics need Studio connected. Native integration requires
root-enabled CB01, ARM32 and LineOS 1.0.8 or 1.0.9. Studio must reconnect to restore
widgets after a Core restart. Installing a package does not deploy it.

This format cannot run Python, JavaScript, EXEs, APKs, custom shaders or arbitrary
new sensor logic. A new renderer/data source needs a host API enhancement first.
Open an Issue with the proposed capability. Standalone APK apps have a separate
manual review path; do not label an APK as an integrated widget.

## 1. Fork and create your submission

1. Sign in to GitHub and open https://github.com/qlerup/ultrabar-store.
2. Click **Fork**, then **Create fork**. Create a branch such as `add-my-clock`.
3. In your fork choose **Add file > Create new file** or **Upload files**.
4. Add these five files under `submissions/my-clock/` (lowercase folder name):

```
submissions/my-clock/
  widget.json
  manifest.json
  icon.png
  README.md
  LICENSE
```

An **icon.png is mandatory**: static PNG, square 256x256 or 512x512 pixels, maximum 256 KiB (262144 bytes). Use your own original or licensed app icon; it is shown on the store card. SVG, animated PNG and other dimensions are rejected. Transparency is allowed. Include rights for the icon in LICENSE.

Copy `examples/clock/widget.json` and `examples/clock/manifest.json` as a starting
point. Use your own stable package ID, name, description and license. Widget IDs
must stay stable between updates. Change the default settings to suit your widget.
Keep `widgetApi: 1` and `runtime: studio-native-v1`.

README.md must describe what the widget does, every setting, supported hardware,
what you tested and any limitations. LICENSE must actually permit store users to
download/use the package and the owner to redistribute it. Submit only files you
have permission to share. No keys, passwords, personal device addresses or IDs. Save JSON as UTF-8 with LF line endings; checksums apply to these exact bytes.
For declarative JSON, widget.json itself is the source; no build tool is needed.

Commit the widget files first. Open that commit and copy its full 40-character
SHA. Set `source` in manifest.json to the immutable file URL:
`https://github.com/YOURNAME/ultrabar-store/blob/COMMIT_SHA/submissions/my-clock/widget.json`.
Commit that manifest change. This two-commit sequence avoids a circular commit hash.

Do not add `artifact` or `icon` download metadata or edit `catalog.json` yet. Upload the actual icon.png alongside your widget files. The owner publishes the final
reviewed bytes under the official store account during review.

## 2. Open the pull request

1. In your fork choose **Contribute > Open pull request**.
2. Set base repository `qlerup/ultrabar-store`, base branch `main`, and compare
   your submission branch.
3. Fill in the template: explain the function, license, compatibility and testing.
   If you have not tested on physical Core, state that plainly.
4. Allow maintainer edits if you want the owner to prepare publication on your
   branch. Otherwise the owner can publish via a separate reviewed branch.
5. Click **Create pull request**.

The **Store submission checks / Validate package** bot runs automatically.
Open **Checks**, select the failed check and read its summary. Fix the files in
this same branch and commit; GitHub reruns the checks. Do not create a new PR for
each fix. Optionally run `python scripts/validate.py .` locally with Python 3.
The bot never executes or builds contributor code. It validates data using the
validator from the trusted main branch, without executing submitted code. Only the trusted comment step receives permission to update the PR comment.

The initial submission reports **Not ready for approval** until the owner has
published the official artifact and added the catalog entry. This publication
step is the owner's responsibility, not something contributors need repository
write access for. The bot distinguishes it in the fixes list.

The bot updates one PR comment with checks, errors and rerun instructions. Fixing
files and pushing a new commit reruns it automatically. The owner can also choose
**Actions > Store submission checks > Run workflow**, enter the PR number, and run
again without changing files. Only **Ready for approval** plus a passing check
means the package has passed automated publication checks. Human acceptance is
still required; nothing is merged automatically.

## 3. Owner review and publication

The owner reviews rights, source, usability, compatibility and testing evidence.
The bot cannot prove visual quality or real-device behavior.

After review, the owner uploads the exact widget.json bytes to a versioned
GitHub Release asset in `qlerup/ultrabar-store` (a review prerelease is fine), then
adds `artifact` to manifest.json with the official URL, byte count and SHA-256.
The owner also publishes icon.png as an official release asset and adds `icon`
with its URL, size and SHA-256. These metadata fields describe different files.
The owner adds the identical manifest to `catalog.json.packages` in the PR.

The bot rechecks the structure and downloads the public JSON asset to verify it
matches the reviewed local file byte-for-byte, and checks the icon can be decoded, has allowed dimensions and matches its own published bytes/checksum. It rejects duplicate IDs,
unsupported settings, missing license/README, mutable source references,
nonofficial artifact URLs and hash/size mismatches. Assets must be publicly
accessible before the final check can pass.

The owner then explicitly merges the PR. Studio refreshes main/catalog.json when
the store opens, on Refresh, and once a minute while visible. GitHub caching can
briefly delay visibility. Users install once, drag, configure and Deploy. No new
Studio release is needed for packages using an already-supported host API.

## Updates and removal

Keep package and widget IDs; increase the semantic version, submit a new PR and
publish a new immutable asset. Never replace an old asset with different bytes.
Library updates do not silently change existing draft/deployed settings. Remove
and add the widget again to adopt new defaults, then Deploy.

Removing a package from the library does not erase placed widgets. Remove the
widget from the layout and Deploy to remove it from Core. Saved drafts/backups
are retained. A catalog removal stops new installs, not existing deployments.
