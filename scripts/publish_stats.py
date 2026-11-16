"""Collect counts once in GitHub Actions; Studio downloads only the public JSON."""
import base64,json,os,re,subprocess,time
from urllib.parse import quote


def identity(package):
    source=re.match(r'https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/(?:blob|tree)/',package.get('source',''))
    artifact=package.get('artifact',{}).get('url','')
    asset=re.fullmatch(r'https://github\.com/qlerup/ultrabar-store/releases/download/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)',artifact)
    if not source or not asset:return None
    return source[1],asset[1],asset[2],artifact


def count(value):
    if type(value) is not int or value<0:raise ValueError('Invalid count')
    return value


def collect(catalog,old,api,now):
    packages=catalog['packages'];identities={p['id']:identity(p) for p in packages}
    repos=sorted({value[0] for value in identities.values() if value})
    issues={};releases={};rows={}
    # A batch reads issue counts excluding PRs without the search API's separate quota.
    for start in range(0,len(repos),20):
        batch=repos[start:start+20]
        query='query {'+''.join('r'+str(i)+':repository(owner:'+json.dumps(repo.split('/')[0])+',name:'+json.dumps(repo.split('/')[1])+'){issues(states:OPEN){totalCount}}' for i,repo in enumerate(batch))+'}'
        try:data=api('graphql','POST',dict(query=query)).get('data') or {}
        except Exception:data={}
        for i,repo in enumerate(batch):
            try:issues[repo]=count(data['r'+str(i)]['issues']['totalCount'])
            except (KeyError,TypeError,ValueError):issues[repo]=None
    for key,value in identities.items():
        if not value:continue
        repo,tag,asset,url=value;previous=old.get('packages',{}).get(key,{})
        if previous.get('repository')!='https://github.com/'+repo or previous.get('artifact')!=url:previous={}
        downloads=None
        if tag not in releases:
            try:releases[tag]=api('repos/qlerup/ultrabar-store/releases/tags/'+quote(tag,safe=''))
            except Exception:releases[tag]=None
        try:downloads=count(next(a['download_count'] for a in releases[tag]['assets'] if a['name']==asset))
        except (KeyError,TypeError,ValueError,StopIteration):pass
        rows[key]=dict(repository='https://github.com/'+repo,artifact=url,
                       downloads=downloads if downloads is not None else previous.get('downloads'),
                       issues=issues[repo] if issues[repo] is not None else previous.get('issues'),
                       stale=downloads is None or issues[repo] is None)
    return dict(schemaVersion=1,generatedAt=int(now),packages=rows)


def main():
    repo=os.environ['GITHUB_REPOSITORY']
    def api(path,method='GET',body=None,optional=False):
        args=['gh','api',path,'--method',method]
        if body is not None:args+=['--input','-']
        result=subprocess.run(args,input=json.dumps(body).encode() if body is not None else None,capture_output=True)
        if result.returncode:
            if optional and b'HTTP 404' in result.stderr:return None
            raise RuntimeError('GitHub statistics request failed')
        return json.loads(result.stdout)
    base='repos/'+repo
    ref=api(base+'/git/ref/heads/catalog')['object']['sha']
    def read(name,optional=False):
        result=api(base+'/contents/'+name+'?ref='+ref,optional=optional)
        return json.loads(base64.b64decode(result['content'])) if result else {}
    catalog=read('catalog.json');old=read('package-stats.json',True);now=time.time()
    expected={p['id']:identity(p) for p in catalog['packages'] if identity(p)}
    if old.get('generatedAt',0)>now-900 and set(old.get('packages',{}))==set(expected) and all(old['packages'][key].get('artifact')==value[3] and old['packages'][key].get('repository')=='https://github.com/'+value[0] for key,value in expected.items()):
        print('Published package counts are current.');return
    stats=collect(catalog,old,api,now)
    commit=api(base+'/git/commits/'+ref)
    tree=api(base+'/git/trees','POST',dict(base_tree=commit['tree']['sha'],tree=[dict(path='package-stats.json',mode='100644',type='blob',content=json.dumps(stats,indent=2)+'\n')]))
    next_commit=api(base+'/git/commits','POST',dict(message='Refresh published package counts',tree=tree['sha'],parents=[ref]))
    if api(base+'/git/ref/heads/catalog')['object']['sha']!=ref:
        print('Catalog changed during count collection; leaving the previous feed intact.');return
    api(base+'/git/refs/heads/catalog','PATCH',dict(sha=next_commit['sha'],force=False))
    stale=sum(bool(p['stale']) for p in stats['packages'].values())
    print('Published counts for '+str(len(stats['packages']))+' packages; '+str(stale)+' retain unavailable or stale counts.')


if __name__=='__main__':main()
