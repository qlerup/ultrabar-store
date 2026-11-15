import copy
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import comment
from studio_contract import manifest_issues
from comment import render_comment


class StudioContractTests(unittest.TestCase):
    def setUp(self):
        self.manifest=dict(schemaVersion=1,id='alice.app',name='App',description='Example',version='1.0.0',type='corebar-app',publisher='alice',license='MIT',source='https://github.com/alice/app/blob/'+'a'*40+'/AndroidManifest.xml',permissions=[],compatibility=dict(hostApi=1,minStudioVersion='0.28.0',models=['CB01'],lineosVersions=['1.0.9'],abis=['armeabi-v7a']),android=dict(packageId='dk.alice.app',versionCode=1,minSdk=26,signerSha256='a'*64))

    def test_supported_app_and_declarative_manifest(self):
        self.assertEqual(manifest_issues(self.manifest),[])
        for kind in ('corebar-widget','studio-plugin'):
            manifest=copy.deepcopy(self.manifest);manifest['type']=kind;del manifest['android']
            self.assertEqual(manifest_issues(manifest),[])

    def test_settings_descriptor_requires_new_studio_and_an_apk(self):
        from test_app_settings_contract import schema
        self.manifest['settings']=schema()
        self.assertTrue(any('0.45.0' in issue for issue in manifest_issues(self.manifest)))
        self.manifest['compatibility']['minStudioVersion']='0.45.0'
        self.assertEqual(manifest_issues(self.manifest),[])
        self.manifest['settings']['fields'][1]['default']=1001
        self.assertTrue(any('settings' in issue for issue in manifest_issues(self.manifest)))

    def test_reports_independent_missing_and_unsupported_fields(self):
        manifest=copy.deepcopy(self.manifest);del manifest['description'];manifest['installScript']='run.sh';manifest['compatibility']['hostApi']=True;manifest['compatibility']['abis']=['arm64-v8a'];manifest['android']['minSdk']=30
        issues=manifest_issues(manifest)
        for name in ('description','installScript','hostApi','abis','minSdk'):
            self.assertTrue(any(name in issue and 'Fix:' in issue for issue in issues),name)

    def test_malformed_nested_values_are_explained(self):
        for field in ('compatibility','permissions','android','artifact','icon'):
            manifest=dict(self.manifest);manifest[field]=None
            self.assertTrue(any(field in issue for issue in manifest_issues(manifest)),field)
        self.assertTrue(manifest_issues([]))

    def test_duplicate_permissions_and_unknown_android_fields_fail(self):
        self.manifest['permissions']=['android.permission.INTERNET']*2
        self.manifest['android']['setupCommand']='sh setup'
        issues=manifest_issues(self.manifest)
        self.assertTrue(any('permissions' in issue for issue in issues))
        self.assertTrue(any('setupCommand' in issue for issue in issues))

    def test_pr_feedback_explains_repairs_and_escapes_submitted_text(self):
        report=render_comment(dict(ready=False,errors=['app.apk: <script>@someone</script> Fix: add launcher.'],notes=[],checks=['APK launch contract']), 'owner/store','123','a'*40)
        self.assertIn('Changes needed',report);self.assertIn('What to fix',report);self.assertIn('Fix: add launcher',report)
        self.assertIn('&lt;script&gt;',report);self.assertNotIn('<script>',report)
        self.assertIn('same PR branch',report);self.assertIn('do **not** run',report)
        self.assertIn('a'*40,report)

    def test_green_checks_are_not_a_hardware_test_or_automatic_new_package_approval(self):
        report=render_comment(dict(ready=True,errors=[],notes=[],checks=[]),'owner/store','123')
        self.assertIn('New packages still require maintainer approval',report)
        self.assertIn('physical Core',report)

    def test_feedback_stays_within_github_comment_limit(self):
        report=render_comment(dict(ready=False,errors=['<&>'*1800]*100,notes=['<&>'*10000],checks=[]),'owner/store','123')
        self.assertLess(len(report),60000);self.assertIn('Full run log',report)

    def test_existing_pr_comment_is_updated_and_newer_head_is_left_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=Path(tmp)/'result.json';result.write_text(json.dumps(dict(ready=False,errors=['app.apk: missing launcher. Fix: add it.'],notes=[],checks=[])))
            requests=[]
            def remote(request,**kwargs):
                import io
                requests.append(request)
                if request.full_url.endswith('/pulls/12'):data=dict(head=dict(sha='a'*40))
                elif '/comments?' in request.full_url:data=[dict(id=7,user=dict(login='github-actions[bot]'),body=comment.MARKER+'old')]
                else:data={}
                return io.BytesIO(json.dumps(data).encode())
            env=dict(PR_NUMBER='12',GITHUB_REPOSITORY='owner/store',GH_TOKEN='test',REVIEW_SHA='a'*40,STORE_RESULT=str(result),GITHUB_RUN_ID='123')
            with patch.dict('os.environ',env),patch.object(comment,'urlopen',side_effect=remote):comment.main()
            self.assertEqual(requests[-1].method,'PATCH');self.assertTrue(requests[-1].full_url.endswith('/issues/comments/7'))
            self.assertIn('missing launcher',json.loads(requests[-1].data)['body'])
            requests.clear()
            with patch.dict('os.environ',dict(env,REVIEW_SHA='b'*40)),patch.object(comment,'urlopen',side_effect=remote):
                with self.assertRaisesRegex(SystemExit,'newer commit'):comment.main()
            self.assertEqual(len(requests),1)
