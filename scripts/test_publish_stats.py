import copy,unittest
from publish_stats import collect,identity


def package(key='widget'):
    return dict(id='studio.'+key,source='https://github.com/owner/'+key+'/blob/'+'a'*40+'/widget.json',artifact=dict(url='https://github.com/qlerup/ultrabar-store/releases/download/review-'+key+'/widget.json'))


class PublishedCountTests(unittest.TestCase):
    def api(self,path,method='GET',body=None):
        if path=='graphql':
            self.assertIn('issues(states:OPEN){totalCount}',body['query'])
            return dict(data={'r0':dict(issues=dict(totalCount=3))})
        self.assertTrue(path.endswith('review-widget'))
        return dict(assets=[dict(name='icon.png',download_count=999),dict(name='widget.json',download_count=17)])

    def test_exact_artifact_and_issue_only_counts(self):
        result=collect(dict(packages=[package()]),{},self.api,123)
        row=result['packages']['studio.widget']
        self.assertEqual((row['downloads'],row['issues']),(17,3));self.assertFalse(row['stale'])
        self.assertEqual(row['artifact'],package()['artifact']['url']);self.assertEqual(result['generatedAt'],123)

    def test_failures_preserve_counts_but_never_reuse_counts_for_another_version(self):
        old=collect(dict(packages=[package()]),{},self.api,123)
        def offline(*args):raise OSError('offline')
        row=collect(dict(packages=[package()]),old,offline,456)['packages']['studio.widget']
        self.assertEqual((row['downloads'],row['issues']),(17,3));self.assertTrue(row['stale'])
        changed=copy.deepcopy(package());changed['artifact']['url']=changed['artifact']['url'].replace('review-widget','review-widget2')
        row=collect(dict(packages=[changed]),old,offline,456)['packages']['studio.widget']
        self.assertIsNone(row['downloads']);self.assertIsNone(row['issues']);self.assertTrue(row['stale'])

    def test_repositories_are_batched_and_release_metadata_is_shared(self):
        rows=[package('widget'+str(i)) for i in range(45)]
        for row in rows:row['artifact']['url']=package()['artifact']['url']
        calls=[]
        def api(path,method='GET',body=None):
            calls.append(path)
            return dict(data={}) if path=='graphql' else dict(assets=[])
        result=collect(dict(packages=rows),{},api,123)
        self.assertEqual(calls.count('graphql'),3);self.assertEqual(len(calls),4);self.assertEqual(len(result['packages']),45)

    def test_untrusted_asset_does_not_trigger_remote_lookup(self):
        p=package();p['artifact']['url']='https://evil.example/file'
        def unexpected(*args):raise AssertionError('Untrusted identity triggered network access')
        self.assertIsNone(identity(p));self.assertEqual(collect(dict(packages=[p]),{},unexpected,123)['packages'],{})
