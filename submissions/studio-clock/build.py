"""Build a release APK; signing key and password file stay outside the repository."""
import argparse,subprocess,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--sdk',type=Path,required=True);p.add_argument('--keystore',type=Path,required=True);p.add_argument('--password-file',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;build=a.output.parent/'clock-build';classes=build/'classes';classes.mkdir(parents=True,exist_ok=True)
bt=a.sdk/'android-15';jar=a.sdk/'android-35/android.jar'
def run(*args):subprocess.run([str(x) for x in args],check=True)
run('javac','-encoding','UTF-8','-source','8','-target','8','-classpath',jar,'-d',classes,*root.glob('src/**/*.java'))
run('java','-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--lib',jar,'--min-api','26','--output',build,*classes.rglob('*.class'))
run(bt/'aapt.exe','package','-f','-M',root/'AndroidManifest.xml','-I',jar,'-S',root/'res','-F',build/'unsigned.apk')
with zipfile.ZipFile(build/'unsigned.apk','a',compression=zipfile.ZIP_DEFLATED) as z:z.write(build/'classes.dex','classes.dex')
run(bt/'zipalign.exe','-f','4',build/'unsigned.apk',build/'aligned.apk')
run('java','-jar',bt/'lib/apksigner.jar','sign','--ks',a.keystore,'--ks-key-alias','studio-clock','--ks-pass','file:'+str(a.password_file),'--v2-signing-enabled','true','--out',a.output,build/'aligned.apk')
run('java','-jar',bt/'lib/apksigner.jar','verify','--verbose','--print-certs',a.output)
