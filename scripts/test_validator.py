import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from validate import validate_tree
class Checks(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.folder=self.root/'submissions'/'clock';self.folder.mkdir(parents=True)
  (self.root/'catalog.json').write_text('{"schemaVersion":1,"packages":[]}')
  for f in ('README.md','LICENSE'):(self.folder/f).write_text('This is explicit test documentation and permission to distribute.')
  self.raw=b'{"widgetApi":1,"runtime":"studio-native-v1","widgets":[{"id":"clock","name":"Clock","kind":"clock"}]}'
  (self.folder/'widget.json').write_bytes(self.raw)
  self.manifest=dict(schemaVersion=1,id='test.clock',name='Test clock',description='Test clock widget',version='1.0.0',type='corebar-widget',license='Test',source='https://github.com/test/repo/blob/'+'a'*40+'/widget.json',permissions=[],compatibility=dict(minStudioVersion='0.20.0',hostApi=1,models=['CB01'],abis=['armeabi-v7a'],lineosVersions=['1.0.9']))
  self.save()
 def save(self): (self.folder/'manifest.json').write_text(json.dumps(self.manifest))
 def test_draft_submission_can_pass_without_publication(self):
  errors,notes=validate_tree(self.root);self.assertEqual(errors,[]);self.assertIn('owner must publish',notes[0])
 def test_catalog_cannot_publish_unreleased_submission(self):
  (self.root/'catalog.json').write_text(json.dumps(dict(schemaVersion=1,packages=[self.manifest])))
  self.assertTrue(validate_tree(self.root)[0])
 def test_final_catalog_and_exact_local_hash(self):
  self.manifest['artifact']=dict(url='https://github.com/qlerup/ultrabar-store/releases/download/v1/widget.json',size=len(self.raw),sha256=hashlib.sha256(self.raw).hexdigest());self.save()
  (self.root/'catalog.json').write_text(json.dumps(dict(schemaVersion=1,packages=[self.manifest])))
  self.assertEqual(validate_tree(self.root)[0],[])
  (self.folder/'widget.json').write_bytes(self.raw+b' ')
  self.assertTrue(validate_tree(self.root)[0])
 def test_no_executable_fields(self):
  value=json.loads(self.raw);value['widgets'][0]['script']='evil()';(self.folder/'widget.json').write_text(json.dumps(value))
  self.assertTrue(validate_tree(self.root)[0])
 def test_missing_license_and_mutable_source_fail(self):
  (self.folder/'LICENSE').unlink();self.assertTrue(validate_tree(self.root)[0])
  (self.folder/'LICENSE').write_text('License text permitting distribution of this test.')
  self.manifest['source']='https://github.com/test/repo/tree/main/widget.json';self.save();self.assertTrue(validate_tree(self.root)[0])
if __name__=='__main__':unittest.main()
