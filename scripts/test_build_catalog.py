import json,tempfile,unittest,subprocess
from pathlib import Path
from build_catalog import build

class CatalogTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'submissions').mkdir()
 def add(self,name,entry):
  folder=self.root/'submissions'/name;folder.mkdir(exist_ok=True)
  (folder/'manifest.json').write_text(json.dumps(entry))
 def test_deterministic_complete_list_and_independent_update(self):
  self.add('z',dict(id='test.z',version='1.0.0'));self.add('a',dict(id='test.a',version='1.0.0'))
  original=build(self.root);self.assertEqual([p['id'] for p in original['packages']],['test.a','test.z'])
  self.add('a',dict(id='test.a',version='1.0.1'))
  self.assertEqual(build(self.root)['packages'][1],original['packages'][1])
  self.assertEqual(build(self.root)['packages'][0]['version'],'1.0.1')
 def test_duplicate_and_invalid_manifest_rejected(self):
  self.add('a',dict(id='test.a'));self.add('b',dict(id='test.a'))
  with self.assertRaisesRegex(ValueError,'Duplicate'):build(self.root)
 def test_separate_package_prs_merge_without_catalog_conflict(self):
  # Real Git merge: two branches edit different packages without a shared list.
  def git(*args):return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.STDOUT)
  git('init','-b','main');git('config','user.name','Test');git('config','user.email','test@example.invalid')
  self.add('one',dict(id='test.one',version='1.0.0'));self.add('two',dict(id='test.two',version='1.0.0'))
  git('add','.');git('commit','-m','initial')
  git('switch','-c','update-one');self.add('one',dict(id='test.one',version='1.0.1'));git('commit','-am','one')
  git('switch','main');git('switch','-c','update-two');self.add('two',dict(id='test.two',version='1.0.2'));git('commit','-am','two')
  git('switch','main');git('merge','update-one');git('merge','update-two','--no-edit')
  self.assertEqual([p['version'] for p in build(self.root)['packages']],['1.0.1','1.0.2'])
