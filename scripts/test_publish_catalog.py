import base64,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import publish_catalog


class PublicationCheckTests(unittest.TestCase):
 def test_catalog_update_preserves_other_published_files_in_base_tree(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'submissions').mkdir();captured=[]
   def api(args,**kwargs):
    path=args[2];method=args[-1] if '--input' not in args else 'POST'
    if path.endswith('/git/ref/heads/main'):data=dict(object=dict(sha='a'*40))
    elif path.endswith('/git/ref/heads/catalog'):data=dict(object=dict(sha='b'*40))
    elif '/git/commits/' in path:data=dict(tree=dict(sha='c'*40))
    elif path.endswith('/git/trees'):
     captured.append(json.loads(kwargs['input']));data=dict(sha='d'*40)
    elif path.endswith('/git/commits'):data=dict(sha='e'*40)
    else:data={}
    return SimpleNamespace(returncode=0,stdout=json.dumps(data).encode(),stderr=b'')
   previous=Path.cwd()
   try:
    os.chdir(root)
    with patch.dict('os.environ',GITHUB_REPOSITORY='owner/store'),patch.object(publish_catalog.subprocess,'check_output',return_value=('a'*40).encode()),patch.object(publish_catalog.subprocess,'run',side_effect=api):publish_catalog.main()
    self.assertEqual(captured[0]['base_tree'],'c'*40)
    self.assertEqual({v['path'] for v in captured[0]['tree']},{'catalog.json','source.json'})
   finally:os.chdir(previous)
 def test_unchanged_source_skips_asset_downloads_and_git_writes(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'submissions').mkdir();output=root/'output'
   def api(args,**kwargs):
    path=args[2]
    data=dict(object=dict(sha='a'*40)) if path.endswith('/git/ref/heads/main') else dict(content=base64.b64encode(json.dumps(dict(sourceCommit='a'*40)).encode()).decode())
    return SimpleNamespace(returncode=0,stdout=json.dumps(data).encode(),stderr=b'')
   previous=Path.cwd()
   try:
    os.chdir(root)
    with patch.dict('os.environ',GITHUB_REPOSITORY='owner/store',GITHUB_OUTPUT=str(output)),patch.object(publish_catalog.subprocess,'check_output',return_value=('a'*40).encode()),patch.object(publish_catalog.subprocess,'run',side_effect=api) as run:
     publish_catalog.main(check_only=True)
     self.assertEqual(run.call_count,2);self.assertTrue(all(call.args[0][-1]=='GET' for call in run.call_args_list))
    self.assertEqual(output.read_text(),'needed=false\n')
   finally:os.chdir(previous)
