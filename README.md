# UltraBar Store

Reviewed widget packages for [UltraBar Studio](https://github.com/qlerup/ultrabar-studio).
One package appears in the widget library: drag it onto Core, configure it in the
right panel, then Deploy. New approved packages appear without updating Studio.

**[Submit a package: step-by-step guide](SUBMIT-A-PACKAGE.md)**

GitHub automatically checks submissions. New packages require owner approval;
eligible updates to registered packages receive bot approval and auto-merge after
green checks. The live catalog is generated from approved package manifests on the `catalog` branch. See CONTRIBUTING.md for the policy.
Studio 0.20 supports clock/date and PC hardware widgets through the shared native
runtime. Arbitrary executable plugins are not supported. See the guide for limits.

Studio's proprietary license does not apply automatically to contributors' work.
Every submitted package must have its own explicit distribution/use license.

Package PRs change only their own submissions folder. Never edit catalog.json: the main-branch copy is a frozen compatibility snapshot. Studio 0.31+ uses the generated feed; see CONTRIBUTING.md for publication and recovery details.
