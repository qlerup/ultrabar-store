import io, json, hashlib, tempfile, unittest, zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import apk_check, repository_check

class ApkReviewTests(unittest.TestCase):
 def test_metadata_and_signature_required(self):
  entry=dict(version='1.0.0',permissions=['android.permission.INTERNET'],android=dict(packageId='dk.test.app',versionCode=1,minSdk=26,signerSha256='a'*64))
  info="package: name='dk.test.app' versionCode='1' versionName='1.0.0'\nsdkVersion:'26'\nuses-permission: name='android.permission.INTERNET'\n"
  signature='Verified using v2 scheme (APK Signature Scheme v2): true\r\nSigner #1 certificate SHA-256 digest: '+'a'*64+'\r\n'
  def result(text,code=0):return SimpleNamespace(returncode=code,stdout=text.encode())
  with patch.dict('os.environ',ANDROID_BUILD_TOOLS='/sdk'),patch.object(apk_check.subprocess,'run',side_effect=[result(info),result(signature)]):apk_check.inspect(Path('app.apk'),entry)
  for bad in (info+'application-debuggable\n',info.replace("versionCode='1'","versionCode='2'"),info.replace('android.permission.INTERNET','android.permission.CAMERA')):
   with patch.dict('os.environ',ANDROID_BUILD_TOOLS='/sdk'),patch.object(apk_check.subprocess,'run',return_value=result(bad)):
    with self.assertRaises(ValueError):apk_check.inspect(Path('app.apk'),entry)
  with patch.dict('os.environ',ANDROID_BUILD_TOOLS='/sdk'),patch.object(apk_check.subprocess,'run',side_effect=[result(info),result(signature,1)]):
   with self.assertRaisesRegex(ValueError,'signature'):apk_check.inspect(Path('app.apk'),entry)
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
