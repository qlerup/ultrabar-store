"""Inspect APK data with trusted Android SDK tools; never execute the APK."""
import os, re, subprocess
from pathlib import Path

def inspect(path, entry):
    root=Path(os.environ['ANDROID_BUILD_TOOLS'])
    suffix='.exe' if os.name=='nt' else ''
    result=subprocess.run([str(root/('aapt'+suffix)), 'dump','badging',str(path)],capture_output=True,timeout=30)
    if result.returncode:raise ValueError('Android SDK could not read app.apk.')
    info=result.stdout.decode('utf-8',errors='replace');meta=entry['android']
    package=re.search(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']*)'",info,re.M)
    sdk=re.search(r"^sdkVersion:'(\d+)'",info,re.M)
    if not package or (package[1],int(package[2]),package[3])!=(meta['packageId'],meta['versionCode'],entry['version']) or not sdk or int(sdk[1])!=meta['minSdk']:raise ValueError('APK ID, version or minimum Android SDK differs from manifest.')
    if 'application-debuggable' in info:raise ValueError('APK must be a non-debuggable release build.')
    permissions=set(re.findall(r"^uses-permission(?:-sdk-\d+)?: name='([^']+)'",info,re.M))
    if permissions!=set(entry['permissions']):raise ValueError('Declare the exact APK Android permissions in manifest.json.')
    result=subprocess.run(['java','-jar',str(root/'lib/apksigner.jar'),'verify','--verbose','--print-certs',str(path)],capture_output=True,timeout=30)
    output=result.stdout.decode(errors='replace').replace('\r\n','\n')
    signers=re.findall(r'^Signer #\d+ certificate SHA-256 digest: ([a-fA-F0-9]+)$',output,re.M)
    if result.returncode or 'Verified using v2 scheme (APK Signature Scheme v2): true' not in output or signers!=[meta['signerSha256']]:raise ValueError('APK signature verification failed or signer differs from approved manifest.')
