# UltraBar Store

The Store distributes reviewed widgets, Core apps and declarative presets for
[UltraBar Studio](https://github.com/qlerup/ultrabar-studio).

## Install and use packages

1. In Studio, open **App & Plugin Store** and install a compatible package.
2. Go to **Design & actions**. Drag widgets from the **App Store** library onto
   the CoreBAR preview. Supported Core apps can also go into **Background apps**.
3. Configure the placed item and choose **Deploy to Core** to review and apply it on CoreBAR.

Studio shows the minimum Studio version required by each package. On root-enabled
ARM32 CB01 with LineOS 1.0.9, compatible widgets can use large or small slots.
Studio 0.52.1 adds **+** on empty slots, where you can choose a 2×2 grid.
See the [Vivo Screen Sync guide](https://github.com/qlerup/vivo-screen-sync#use)
for the background app setup.

## Submit a package

Keep the source in your own public repository, publish a stable release and
open one Store pull request for that package. Use the [submission guide](SUBMIT-A-PACKAGE.md)
for required files, compatibility and declaring supported widget sizes.
For editable Studio settings, see the [integration requirements](APP-SETTINGS.md)
and the [complete Android example](examples/settings-app).

GitHub Actions validates package metadata, upstream ownership and published bytes.
New packages require maintainer acceptance. Eligible updates to registered
packages can auto-merge after successful checks. Each package needs its own
distribution license. See [CONTRIBUTING.md](CONTRIBUTING.md) for review policy.

## Published catalog

The publication workflow generates the live catalog from approved manifests on
the `catalog` branch. The main-branch copy of `catalog.json` is a frozen
compatibility snapshot. Package PRs change only their own submission folder.

Studio fetches the public catalog, immutable package files and the separate
`catalog/package-stats.json` snapshot directly. GitHub Actions collects download
and issue counts centrally. Unavailable counts retain their previous values
and package installation can proceed.
