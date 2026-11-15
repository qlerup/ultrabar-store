import io, json, hashlib, tempfile, unittest, zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import apk_check, repository_check

class ApkReviewTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.apk=Path(self.temp.name)/'app.apk'
  with zipfile.ZipFile(self.apk,'w') as z:z.writestr('classes.dex',b'dex\n035\0'+b'\0'*104)
 def test_metadata_and_signature_required(self):
  entry=dict(version='1.0.0',permissions=['android.permission.INTERNET'],android=dict(packageId='dk.test.app',versionCode=1,minSdk=26,signerSha256='a'*64))
  info="package: name='dk.test.app' versionCode='1' versionName='1.0.0'\nsdkVersion:'26'\nuses-permission: name='android.permission.INTERNET'\nlaunchable-activity: name='dk.test.app.MainActivity'\n"
  xml='E: manifest\n  E: application\n    E: activity\n      A: android:name(0x01010003)=".MainActivity"\n      A: android:exported(0x01010010)=(type 0x12)0xffffffff\n'
  signature='Verified using v2 scheme (APK Signature Scheme v2): true\r\nSigner #1 certificate SHA-256 digest: '+'a'*64+'\r\n'
  def result(text,code=0):return SimpleNamespace(returncode=code,stdout=text.encode())
  with patch.dict('os.environ',ANDROID_BUILD_TOOLS='/sdk'),patch.object(apk_check.subprocess,'run',side_effect=[result(info),result(xml),result(signature)]):apk_check.inspect(self.apk,entry)
  for bad in (info+'application-debuggable\n',info.replace("versionCode='1'","versionCode='2'"),info.replace('android.permission.INTERNET','android.permission.CAMERA')):
   with patch.dict('os.environ',ANDROID_BUILD_TOOLS='/sdk'),patch.object(apk_check.subprocess,'run',return_value=result(bad)):
    with self.assertRaises(ValueError):apk_check.inspect(self.apk,entry)
  with patch.dict('os.environ',ANDROID_BUILD_TOOLS='/sdk'),patch.object(apk_check.subprocess,'run',side_effect=[result(info),result(xml),result(signature,1)]):
   with self.assertRaisesRegex(ValueError,'signature'):apk_check.inspect(self.apk,entry)
 def test_missing_launcher_wrong_abi_and_dex_report_all_fixes(self):
  with zipfile.ZipFile(self.apk,'w') as z:z.writestr('resource.txt',b'not code')
  issues=apk_check.studio_issues(self.apk,"native-code: 'arm64-v8a'\n",dict(compatibility=dict(abis=['armeabi-v7a'])))
  self.assertEqual(len(issues),3)
  self.assertTrue(all('Fix:' in issue for issue in issues));self.assertIn('64-bit-only',issues[1])
 def test_pure_java_and_arm32_apks_cover_declared_abi(self):
  for native in ('',"native-code: 'arm64-v8a' 'armeabi-v7a'\n"):
   self.assertEqual(apk_check.studio_issues(self.apk,"launchable-activity: name='dk.test.app.MainActivity'\n"+native,dict(compatibility=dict(abis=['armeabi-v7a']))),[])
 def test_exported_enabled_launcher_and_alias(self):
  info="launchable-activity: name='dk.test.app.Main'\n"
  xml='E: manifest\n  E: application\n    E: activity\n      A: android:name(0x01010003)=".Main"\n      A: android:exported(0x01010010)=(type 0x12)0xffffffff\n'
  self.assertEqual(apk_check.launcher_issues(xml,info,'dk.test.app'),[])
  protected=xml+'      A: android:permission(0x01010006)="dk.test.PRIVATE"\n'
  self.assertIn('permission',apk_check.launcher_issues(protected,info,'dk.test.app')[0])
  for bad in (xml.replace('0xffffffff','0x0'),xml.replace('    E: activity','    A: android:enabled(0x0101000e)=(type 0x12)0x0\n    E: activity'),xml.replace('android:exported','android:enabled')):
   if bad==xml.replace('android:exported','android:enabled'):bad=bad.replace('0xffffffff','0x0')
   self.assertTrue(apk_check.launcher_issues(bad,info,'dk.test.app'))
  alias=xml+'''    E: activity-alias
      A: android:name(0x01010003)=".Alias"
      A: android:targetActivity(0x01010202)=".Main"
      A: android:exported(0x01010010)=(type 0x12)0xffffffff
'''
  self.assertEqual(apk_check.launcher_issues(alias,info.replace('.Main','.Alias'),'dk.test.app'),[])
  self.assertTrue(apk_check.launcher_issues(alias.replace('=".Main"','=".Missing"',1),info.replace('.Main','.Alias'),'dk.test.app'))
 def test_source_archive_matches_every_tracked_file_and_release(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);source=b'public source';(root/'app.apk').write_bytes(b'apk')
   with zipfile.ZipFile(root/'source.zip','w') as z:
    z.writestr('src/',b'')  # git archive includes directory entries.
    z.writestr('AndroidManifest.xml',source)
   tree=dict(tree=[dict(path='AndroidManifest.xml',type='blob',mode='100644',sha=hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest())])
   def remote(req,**kwargs):return io.BytesIO((root/req.full_url.split('/')[-1]).read_bytes())
   with patch.object(repository_check,'get_json',return_value=tree),patch.object(repository_check,'urlopen',side_effect=remote):
    repository_check.verify_apk_source(root,'alice/app','a'*40,'v1.0.0')
    tree['tree'][0]['sha']='b'*40
    with self.assertRaisesRegex(ValueError,'differs'):repository_check.verify_apk_source(root,'alice/app','a'*40,'v1.0.0')
 def test_registration_type_must_match(self):
  link=dict(repository='alice/app',commit='a'*40,release='v1.0.0',type='corebar-app')
  manifest=dict(publisher='alice',type='corebar-app',source='https://github.com/alice/app/blob/'+'a'*40+'/AndroidManifest.xml')
  repository_check.validate_link(link,manifest,'alice')
  with self.assertRaisesRegex(ValueError,'type'):repository_check.validate_link(link,dict(manifest,type='corebar-widget'),'alice')
