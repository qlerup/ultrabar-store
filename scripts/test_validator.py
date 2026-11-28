import copy,hashlib,json,tempfile,unittest,io
from PIL import Image
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
  self.manifest=dict(publisher='test',schemaVersion=1,id='test.clock',name='Test clock',description='Test clock widget',version='1.0.0',type='corebar-widget',license='Test',source='https://github.com/test/repo/blob/'+'a'*40+'/widget.json',permissions=[],compatibility=dict(minStudioVersion='0.20.0',hostApi=1,models=['CB01'],abis=['armeabi-v7a'],lineosVersions=['1.0.9']))
  image=io.BytesIO();Image.new('RGB',(256,256),'#b8adff').save(image,format='PNG');self.icon=image.getvalue();(self.folder/'icon.png').write_bytes(self.icon)
  self.manifest['icon']=dict(url='https://github.com/qlerup/ultrabar-store/releases/download/v1/icon.png',size=len(self.icon),sha256=hashlib.sha256(self.icon).hexdigest())
  self.save()
 def save(self): (self.folder/'manifest.json').write_text(json.dumps(self.manifest))
 def test_draft_submission_needs_owner_publication(self):
  errors,notes=validate_tree(self.root);self.assertTrue(errors);self.assertIn('owner must publish',notes[0])
 def test_catalog_cannot_publish_unreleased_submission(self):
  (self.root/'catalog.json').write_text(json.dumps(dict(schemaVersion=1,packages=[self.manifest])))
  self.assertTrue(validate_tree(self.root)[0])
 def test_final_catalog_and_exact_local_hash(self):
  self.manifest['artifact']=dict(url='https://github.com/qlerup/ultrabar-store/releases/download/v1/widget.json',size=len(self.raw),sha256=hashlib.sha256(self.raw).hexdigest());self.save()
  (self.root/'catalog.json').write_text(json.dumps(dict(schemaVersion=1,packages=[self.manifest])))
  self.assertEqual(validate_tree(self.root)[0],[])
  (self.folder/'widget.json').write_bytes(self.raw+b' ')
  self.assertTrue(validate_tree(self.root)[0])
 def test_widget_payload_size_limit(self):
  payload=self.raw.ljust(128*1024)
  path=self.folder/'widget.json'
  path.write_bytes(payload)
  self.manifest['compatibility']['minStudioVersion']='0.52.47'
  self.manifest['artifact']=dict(url='https://github.com/qlerup/ultrabar-store/releases/download/v1/widget.json',size=len(payload),sha256=hashlib.sha256(payload).hexdigest())
  self.save()
  self.assertEqual(validate_tree(self.root,generated_catalog=True)[0],[])
  path.write_bytes(payload+b' ')
  errors,_=validate_tree(self.root,generated_catalog=True)
  self.assertTrue(any('oversized' in e for e in errors))
 def test_generated_catalog_uses_manifests_without_editing_shared_file(self):
  self.manifest['artifact']=dict(url='https://github.com/qlerup/ultrabar-store/releases/download/v1/widget.json',size=len(self.raw),sha256=hashlib.sha256(self.raw).hexdigest());self.save()
  # Stale legacy snapshots are deliberately excluded from the new live list.
  (self.root/'catalog.json').write_text('obsolete snapshot')
  self.assertEqual(validate_tree(self.root,generated_catalog=True)[0],[])
  self.manifest['artifact']['sha256']='a'*64;self.save()
  self.assertTrue(validate_tree(self.root,generated_catalog=True)[0])
 def test_missing_or_wrong_size_icon_fails(self):
  (self.folder/'icon.png').unlink();self.assertTrue(validate_tree(self.root)[0])
  Image.new('RGB',(128,128)).save(self.folder/'icon.png');self.assertTrue(validate_tree(self.root)[0])
 def test_no_executable_fields(self):
  value=json.loads(self.raw);value['widgets'][0]['script']='evil()';(self.folder/'widget.json').write_text(json.dumps(value))
  self.assertTrue(validate_tree(self.root)[0])
 def test_missing_license_and_mutable_source_fail(self):
  (self.folder/'LICENSE').unlink();self.assertTrue(validate_tree(self.root)[0])
  (self.folder/'LICENSE').write_text('License text permitting distribution of this test.')
  self.manifest['source']='https://github.com/test/repo/tree/main/widget.json';self.save();self.assertTrue(validate_tree(self.root)[0])
 def test_reports_all_missing_files_and_contract_problems_together(self):
  for name in ('LICENSE','README.md','icon.png'):(self.folder/name).unlink()
  self.manifest['compatibility']['hostApi']=2;self.manifest['android']={};self.save()
  errors,_=validate_tree(self.root,generated_catalog=True)
  for name in ('LICENSE','README.md','icon.png','hostApi','android'):
   self.assertTrue(any(name in error and 'Fix:' in error for error in errors),name)
 def test_boolean_plugin_api_is_not_an_integer_api(self):
  from validate import plugin_templates,StoreError
  with self.assertRaises(StoreError):plugin_templates(b'{"pluginApi":true,"widgets":[{"name":"Clock","kind":"clock"}]}')
if __name__=='__main__':unittest.main()

class MeasurementOptions(unittest.TestCase):
 def test_supported_options_and_invalid_choices(self):
  from validate import widget_package, StoreError
  w=dict(id='system',name='System',kind='cpu',kindOptions=['cpu','memory','gpu'])
  def parse(row):return widget_package(json.dumps(dict(widgetApi=1,runtime='studio-native-v1',widgets=[row])).encode())
  self.assertEqual(parse(w)[0]['kindOptions'],w['kindOptions'])
  for options in ([],['cpu'],['cpu','cpu'],['clock','cpu'],['memory','gpu'],'cpu'):
   with self.assertRaises(StoreError):parse(dict(w,kindOptions=options))
