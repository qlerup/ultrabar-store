import json,tempfile,unittest
from pathlib import Path
from build_catalog import build
from listing import state
from removal_request import verify
from repository_check import run
from auto_update import eligibility


class ListingTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)/'base';self.head=Path(self.tmp.name)/'head'
  self.folder='submissions/test'
  for root in (self.base,self.head):
   folder=root/self.folder;folder.mkdir(parents=True)
   (root/'catalog.json').write_text('{}')
   (folder/'manifest.json').write_text(json.dumps(dict(id='alice.test',version='1.0.0',type='corebar-widget',publisher='alice')))
   (folder/'repository.json').write_text(json.dumps(dict(repository='alice/test',type='corebar-widget')))
 def change(self,listed=False):
  (self.head/self.folder/'listing.json').write_text(json.dumps(dict(listed=listed,reason='Owner request')))
 def test_delisting_preserves_registration_and_can_be_restored(self):
  self.assertEqual(len(build(self.head)['packages']),1);self.change()
  self.assertEqual(build(self.head)['packages'],[])
  self.assertTrue((self.head/self.folder/'repository.json').exists())
  self.change(True);self.assertEqual(len(build(self.head)['packages']),1)
 def test_owner_and_maintainer_can_request_removal_without_version_bump(self):
  self.change()
  for author in ('alice','qlerup'):
   errors,_=run(self.head,self.base,dict(user=dict(login=author)));self.assertEqual(errors,[])
  errors,_=run(self.head,self.base,dict(user=dict(login='bob')));self.assertTrue(errors)
 def test_restore_requires_maintainer_and_never_auto_merges(self):
  self.change(True)
  self.assertTrue(run(self.head,self.base,dict(user=dict(login='alice')))[0])
  self.assertFalse(eligibility(self.base,self.head,'alice',[self.folder+'/listing.json'])[0])
 def test_issue_owner_verification(self):
  self.assertTrue(verify(self.base,'alice.test','Alice')[0])
  self.assertFalse(verify(self.base,'alice.test','bob')[0]);self.assertFalse(verify(self.base,'missing.test','alice')[0])
 def test_bad_listing_state_blocks_publication(self):
  (self.head/self.folder/'listing.json').write_text('{"listed":"false","reason":"test"}')
  with self.assertRaises(ValueError):build(self.head)
