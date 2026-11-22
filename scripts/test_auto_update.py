import copy,json,tempfile,unittest
from pathlib import Path
from auto_update import eligibility
from unittest.mock import patch
import auto_update

class UpdatePolicyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.base=Path(self.tmp.name)/'base';self.head=Path(self.tmp.name)/'head'
  self.prefix='submissions/test/'
  self.old=dict(id='alice.widget',type='corebar-widget',publisher='alice',permissions=[],compatibility=dict(hostApi=1,minStudioVersion='0.20.0'),license='Test',version='1.0.0')
  self.new=dict(self.old,version='1.0.1')
  self.link=dict(repository='alice/widget',type='corebar-widget',release='v1.0.0',commit='a'*40)
  self.paths=[self.prefix+'manifest.json',self.prefix+'repository.json',self.prefix+'widget.json']
  self.save()
 def save(self,link=None):
  for root,manifest,registration in ((self.base,self.old,self.link),(self.head,self.new,link or self.link)):
   folder=root/self.prefix;folder.mkdir(parents=True,exist_ok=True)
   (folder/'manifest.json').write_text(json.dumps(manifest))
   (folder/'repository.json').write_text(json.dumps(registration))
   (root/'catalog.json').write_text(json.dumps(dict(schemaVersion=1,packages=[manifest])))
 def check(self,author='alice',paths=None):return eligibility(self.base,self.head,author,paths or self.paths)[0]
 def test_existing_owner_update_qualifies(self):self.assertTrue(self.check())
 def test_validated_native_panel_change_qualifies(self):
  old=dict(widgetApi=1,runtime='studio-native-v1',widgets=[dict(id='clock',kind='clock')])
  new=copy.deepcopy(old);new['widgets'][0]['studio']=dict(api=1,help='New fields')
  for root,widget in ((self.base,old),(self.head,new)):
   (root/self.prefix/'widget.json').write_text(json.dumps(widget))
  self.assertTrue(self.check())
  (self.base/self.prefix/'widget.json').write_text(json.dumps(new))
  self.assertTrue(self.check())
 def test_validated_settings_contract_change_qualifies(self):
  self.new['settings']=dict(api=1,fields=[]);self.save();self.assertTrue(self.check())
 def test_new_or_legacy_package_stays_manual(self):
  (self.base/self.prefix/'repository.json').unlink();self.assertFalse(self.check())
 def test_new_package_cannot_use_unapproved_folder_as_history(self):
  (self.base/self.prefix/'manifest.json').unlink();self.assertFalse(self.check())
 def test_wrong_author_or_owner_transfer_stays_manual(self):
  self.assertFalse(self.check('bob'));self.save(dict(self.link,repository='alice/another'));self.assertFalse(self.check())
 def test_permission_identity_compatibility_changes_stay_manual(self):
  for field,value in (('permissions',['INTERNET']),('id','alice.another'),('publisher','bob'),('type','studio-plugin'),('compatibility',{'hostApi':2}),('license','Changed'),('version','1.0.0')):
   self.new=dict(self.old,version='1.0.1');self.new[field]=value;self.save();self.assertFalse(self.check(),field)
 def test_workflow_other_package_and_unknown_files_stay_manual(self):
  for path in ('.github/workflows/validate.yml','submissions/other/widget.json',self.prefix+'script.sh'):
   self.assertFalse(self.check(paths=self.paths+[path]),path)
 def test_unrelated_catalog_edit_stays_manual(self):
  self.assertFalse(self.check(paths=self.paths+['catalog.json']))
 def test_apk_update_preserves_signer_and_identity(self):
  self.old.update(type='corebar-app',android=dict(packageId='dk.alice.app',signerSha256='a'*64,minSdk=26,versionCode=1));self.link['type']='corebar-app'
  self.new=copy.deepcopy(self.old);self.new['version']='1.0.1';self.new['android']['versionCode']=2;self.save()
  paths=[self.prefix+'manifest.json',self.prefix+'app.apk']
  self.assertTrue(self.check(paths=paths))
  self.new['android']['signerSha256']='b'*64;self.save();self.assertFalse(self.check(paths=paths))
 def invoke(self,change=None,reviews=None):
  pr=dict(state='open',draft=False,head=dict(sha='h'*40),base=dict(ref='main',sha='b'*40),user=dict(login='alice'),labels=[])
  if change:change(pr)
  calls=[]
  def api(args,input=None):
   calls.append((args,json.loads(input) if input else None))
   if args[4]=='POST':return b'{}'
   return json.dumps(reviews or [] if '/reviews' in args[2] else pr).encode()
  def git(root,*args):
   if args[0]=='rev-parse':return (('b' if root==self.base else 'h')*40).encode()
   return b''.join(b':100644 100644 1234567 7654321 M\0'+path.encode()+b'\0' for path in self.paths)
  env=dict(GITHUB_REPOSITORY='owner/store',PR_NUMBER='12',REVIEW_SHA='h'*40,REVIEW_BASE_SHA='b'*40)
  with patch.dict('os.environ',env),patch('sys.argv',['auto_update.py',str(self.base),str(self.head)]),patch.object(auto_update,'git',side_effect=git),patch.object(auto_update.subprocess,'check_output',side_effect=api),patch.object(auto_update.subprocess,'run') as merge:
   auto_update.main();return calls,merge.call_args
 def test_bot_approval_and_merge_pin_validated_head(self):
  calls,merge=self.invoke()
  approval=[body for args,body in calls if args[4]=='POST'][0]
  self.assertEqual(approval['commit_id'],'h'*40);self.assertEqual(approval['event'],'APPROVE')
  self.assertIn('--auto',merge.args[0]);self.assertEqual(merge.args[0][-1],'h'*40)
 def test_changed_head_base_draft_and_manual_label_do_not_approve(self):
  for change in (lambda p:p['head'].update(sha='x'*40),lambda p:p['base'].update(sha='x'*40),lambda p:p.update(draft=True),lambda p:p.update(labels=[dict(name='store-manual-review')])):
   calls,merge=self.invoke(change);self.assertIsNone(merge);self.assertFalse(any(args[4]=='POST' for args,body in calls))
 def test_requested_changes_and_new_package_do_not_approve(self):
  calls,merge=self.invoke(reviews=[dict(state='CHANGES_REQUESTED',user=dict(login='reviewer'))]);self.assertIsNone(merge)
  (self.base/self.prefix/'repository.json').unlink()
  calls,merge=self.invoke();self.assertIsNone(merge);self.assertFalse(any(args[4]=='POST' for args,body in calls))
