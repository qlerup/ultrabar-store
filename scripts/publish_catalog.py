"""Publish a generated data-only branch. Leave the last good catalog on failure."""
import base64,json,os,subprocess
from pathlib import Path
import importlib.util


def main(check_only=False):
    spec=importlib.util.spec_from_file_location('trusted_catalog',Path(__file__).with_name('build_catalog.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    catalog=module.build(Path('.'))
    source=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
    repo=os.environ['GITHUB_REPOSITORY']
    def api(path,method='GET',body=None,optional=False):
        args=['gh','api','repos/'+repo+path,'--method',method]
        if body is not None:args+=['--input','-']
        result=subprocess.run(args,input=json.dumps(body).encode() if body is not None else None,capture_output=True)
        if result.returncode:
            if optional and b'HTTP 404' in result.stderr:return None
            raise RuntimeError('GitHub catalog publication failed: '+result.stderr.decode(errors='replace'))
        return json.loads(result.stdout)
    if api('/git/ref/heads/main')['object']['sha']!=source:
        if check_only and os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'],'a') as output:output.write('needed=false\n')
        print('Main advanced; the newer queued run will publish the latest approved packages.');return
    if check_only:
        metadata=api('/contents/source.json?ref=catalog',optional=True)
        published=json.loads(base64.b64decode(metadata['content'])) if metadata else {}
        needed=published.get('sourceCommit')!=source
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'],'a') as output:output.write('needed='+str(needed).lower()+'\n')
        print('Catalog publication required.' if needed else 'Catalog is current; skipping artifact downloads and inspection.')
        return
    ref=api('/git/ref/heads/catalog',optional=True)
    previous=api('/git/commits/'+ref['object']['sha']) if ref else None
    tree_body=dict(tree=[dict(path='catalog.json',mode='100644',type='blob',content=json.dumps(catalog,indent=2)+'\n'),dict(path='source.json',mode='100644',type='blob',content=json.dumps(dict(sourceCommit=source))+'\n')])
    if previous:tree_body['base_tree']=previous['tree']['sha']
    tree=api('/git/trees','POST',tree_body)
    if ref:
        if previous['tree']['sha']==tree['sha']:
            print('Catalog is already current.');return
    commit=api('/git/commits','POST',dict(message='Generate Store catalog from '+source,tree=tree['sha'],parents=[ref['object']['sha']] if ref else []))
    if api('/git/ref/heads/main')['object']['sha']!=source:
        print('Main advanced during publication; leaving the last catalog intact.');return
    if ref:api('/git/refs/heads/catalog','PATCH',dict(sha=commit['sha'],force=False))
    else:api('/git/refs','POST',dict(ref='refs/heads/catalog',sha=commit['sha']))
    print('Published '+str(len(catalog['packages']))+' approved packages from '+source)


if __name__=='__main__':
    import sys
    main(check_only='--check' in sys.argv)
