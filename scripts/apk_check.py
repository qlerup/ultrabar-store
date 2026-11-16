"""Inspect APK data with trusted Android SDK tools; never execute the APK."""
import os, re, subprocess, zipfile
from pathlib import Path

def launcher_issues(xml,info,package_id):
    """Read trusted aapt's compiled-manifest dump, never source-supplied XML."""
    roots=[];stack=[]
    for line in xml.splitlines():
        element=re.match(r'(\s*)E: ([\w-]+)',line)
        if element:
            indent=len(element[1]);node=dict(tag=element[2],attrs={},children=[])
            while stack and stack[-1][0]>=indent:stack.pop()
            (stack[-1][1]['children'] if stack else roots).append(node);stack.append((indent,node))
        attribute=re.match(r'\s*A: (?:android:)?([\w-]+)(?:\(0x[0-9a-f]+\))?=(.*)',line)
        if attribute and stack:stack[-1][1]['attrs'][attribute[1]]=attribute[2]
    def qualified(raw):
        match=re.match(r'"([^"]+)"',raw or '')
        if not match:return None
        name=match[1];return package_id+name if name.startswith('.') else name if '.' in name else package_id+'.'+name
    def disabled(node):return bool(re.match(r'\(type 0x12\)0x0\b',node['attrs'].get('enabled','')))
    manifest=next((n for n in roots if n['tag']=='manifest'),None)
    app=next((n for n in manifest['children'] if n['tag']=='application'),None) if manifest else None
    if app is None:return ['app.apk / AndroidManifest.xml: Cannot inspect the compiled application. Fix: build a complete APK with an application and a launchable activity.']
    launchable=re.search(r"^launchable-activity: name='([^']+)'",info,re.M)
    if not launchable:return []  # The missing launcher is reported by studio_issues.
    node=next((n for n in app['children'] if n['tag'] in ('activity','activity-alias') and qualified(n['attrs'].get('name'))==launchable[1]),None)
    if node is None:return ['app.apk / AndroidManifest.xml: Launcher component could not be matched to the compiled manifest. Fix: declare a standard MAIN/LAUNCHER activity or activity-alias and rebuild.']
    target=None
    if node['tag']=='activity-alias':target=next((n for n in app['children'] if n['tag']=='activity' and qualified(n['attrs'].get('name'))==qualified(node['attrs'].get('targetActivity'))),None)
    if disabled(app) or disabled(node) or (target is not None and disabled(target)) or re.match(r'\(type 0x12\)0x0\b',node['attrs'].get('exported','')) or (node['tag']=='activity-alias' and target is None):
        return ['app.apk / AndroidManifest.xml: The launcher is disabled, not exported, or targets a missing/disabled activity. Fix: enable the application and launcher, export the launcher so Core can start it, and rebuild the signed release APK.']
    permission=node['attrs'].get('permission',app['attrs'].get('permission',''))
    if permission and not permission.startswith('""'):
        return ['app.apk / AndroidManifest.xml: The launcher requires a permission not guaranteed to Core/Studio. Fix: expose an unprotected MAIN/LAUNCHER entry point (sensitive services can remain protected), or arrange a trusted Studio integration before submission.']
    return []

def studio_issues(path,info,entry):
    issues=[]
    def problem(message,fix):issues.append('app.apk: '+message+' Fix: '+fix)
    if not re.search(r"^launchable-activity: name='[^']+'",info,re.M):
        problem('Studio cannot find a launchable activity.','Add an enabled launcher activity with android.intent.action.MAIN and android.intent.category.LAUNCHER, exported so Core can start it. Rebuild and sign the APK; a service-only APK requires a trusted Studio integration.')
    maximum=re.search(r"^maxSdkVersion:'(\d+)'",info,re.M)
    if maximum and int(maximum[1])<29:problem('maxSdkVersion excludes the supported CB01 Android API 29 runtime.','Remove the unnecessary maxSdkVersion restriction or support API 29, then rebuild and test.')
    native=re.search(r'^native-code:\s*(.*)$',info,re.M)
    actual=set(re.findall(r"'([^']+)'",native[1])) if native else set()
    declared=entry.get('compatibility',{}).get('abis',[])
    if actual and any(abi not in actual for abi in declared):
        problem('Native libraries do not cover compatibility.abis (APK: '+', '.join(sorted(actual))+').','Build/package native libraries for every declared ABI, including armeabi-v7a for CB01. A 64-bit-only APK cannot run on ARM32.')
    try:
        with zipfile.ZipFile(path) as archive:
            dex=archive.getinfo('classes.dex')
            with archive.open(dex) as stream:header=stream.read(112)
            if dex.file_size<112 or not header.startswith(b'dex\n') or header[7:8]!=b'\0':problem('The APK has no usable classes.dex header.','Package the compiled Android application DEX; do not upload a resource-only APK or source archive.')
    except (OSError,ValueError,KeyError,zipfile.BadZipFile):problem('Missing or unreadable classes.dex.','Build the complete release APK with application code, then upload it as app.apk.')
    return issues

def inspect(path, entry):
    import importlib.util
    spec=importlib.util.spec_from_file_location('trusted_bundle',Path(__file__).with_name('bundle_contract.py'))
    bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
    embedded=bundle.inspect_apk(path,entry)
    contract=None
    if 'settings' in entry:
        import importlib.util
        spec=importlib.util.spec_from_file_location('trusted_settings',Path(__file__).with_name('app_settings_contract.py'))
        contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
        contract.inspect_apk(path,entry['settings'])
    root=Path(os.environ['ANDROID_BUILD_TOOLS'])
    suffix='.exe' if os.name=='nt' else ''
    result=subprocess.run([str(root/('aapt'+suffix)), 'dump','badging',str(path)],capture_output=True,timeout=30)
    if result.returncode:raise ValueError('app.apk: Android SDK could not read the APK. Fix: upload a complete compiled release APK, not source, an Android App Bundle or a renamed ZIP.')
    info=result.stdout.decode('utf-8',errors='replace');meta=entry['android']
    issues=studio_issues(path,info,entry)
    package=re.search(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']*)'",info,re.M)
    sdk=re.search(r"^sdkVersion:'(\d+)'",info,re.M)
    if not package or (package[1],int(package[2]),package[3])!=(meta['packageId'],meta['versionCode'],entry['version']) or not sdk or int(sdk[1])!=meta['minSdk']:issues.append('app.apk / manifest.json: APK ID, version or minimum Android SDK differs from manifest. Fix: copy packageId, versionCode, versionName (manifest version) and minSdk from the signed APK; rebuild if those APK values are wrong.')
    if 'application-debuggable' in info:issues.append('app.apk: APK must be a non-debuggable release build. Fix: disable android:debuggable, build the release variant and sign it with your release key.')
    permissions=set(re.findall(r"^uses-permission(?:-sdk-\d+)?: name='([^']+)'",info,re.M))
    if permissions!=set(entry['permissions']):issues.append('manifest.json / permissions: APK permissions differ (missing from manifest: '+', '.join(sorted(permissions-set(entry['permissions'])))+'; not requested by APK: '+', '.join(sorted(set(entry['permissions'])-permissions))+'). Fix: declare the exact APK Android permissions, removing unused permissions from the app before rebuilding.')
    manifest=subprocess.run([str(root/('aapt'+suffix)),'dump','xmltree',str(path),'AndroidManifest.xml'],capture_output=True,timeout=30)
    if manifest.returncode:issues.append('app.apk: Cannot inspect compiled AndroidManifest.xml. Fix: build and upload a complete signed APK.')
    else:issues.extend(launcher_issues(manifest.stdout.decode('utf-8',errors='replace'),info,meta['packageId']))
    if contract and not manifest.returncode:
        try:contract.validate_receiver(manifest.stdout.decode('utf-8',errors='replace'),meta['packageId'])
        except ValueError as exc:issues.append(str(exc))
    result=subprocess.run(['java','-jar',str(root/'lib/apksigner.jar'),'verify','--verbose','--print-certs',str(path)],capture_output=True,timeout=30)
    output=result.stdout.decode(errors='replace').replace('\r\n','\n')
    signers=re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([a-fA-F0-9]+)$',output,re.M)
    if result.returncode or 'Verified using v2 scheme (APK Signature Scheme v2): true' not in output or [s.lower() for s in signers]!=[meta['signerSha256']]:issues.append('app.apk / android.signerSha256: APK signature verification failed or signer differs from approved manifest. Fix: sign with APK Signature Scheme v2, declare the release certificate SHA-256, and keep the approved signing key for updates.')
    if issues:raise ValueError('\n'.join(issues))
    return embedded
