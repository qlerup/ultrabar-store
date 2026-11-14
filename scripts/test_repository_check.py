import unittest
from repository_check import validate_link
class OwnershipTests(unittest.TestCase):
 def setUp(self):
  self.link=dict(repository='alice/widget',commit='a'*40,release='v1.0.0')
  self.manifest=dict(source='https://github.com/alice/widget/blob/'+'a'*40+'/widget.json')
 def test_owner_can_submit(self):self.assertEqual(validate_link(self.link,self.manifest,'Alice')[0],'alice/widget')
 def test_fork_owner_cannot_update_someone_elses_package(self):
  with self.assertRaisesRegex(ValueError,'Only'):validate_link(self.link,self.manifest,'bob')
 def test_cannot_repoint_approved_repository(self):
  with self.assertRaisesRegex(ValueError,'ownership'):validate_link(self.link,self.manifest,'alice',dict(repository='original/widget'))
 def test_source_must_match_pinned_commit(self):
  with self.assertRaisesRegex(ValueError,'source'):validate_link(self.link,dict(source='https://github.com/alice/widget/blob/main/widget.json'),'alice')
 def test_reject_malformed_repository_and_commit(self):
  for change in (dict(repository='alice/../evil'),dict(commit='main'),dict(release='../x')):
   with self.assertRaises(ValueError):validate_link(dict(self.link,**change),self.manifest,'alice')

 def test_multiple_package_changes_rejected(self):
  import tempfile
  from pathlib import Path
  from repository_check import run
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'pr';base=Path(tmp)/'base';(base/'submissions').mkdir(parents=True)
   for name in ('one','two'):
    folder=root/'submissions'/name;folder.mkdir(parents=True);(folder/'widget.json').write_text('{}')
   errors,_=run(root,base,dict(user=dict(login='qlerup')))
   self.assertIn('only one',errors[0])
