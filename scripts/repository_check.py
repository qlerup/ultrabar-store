"""Trusted PR ownership and pinned upstream checks; submitted files are data only."""
import json,os,re,sys,hashlib
from pathlib import Path
from urllib.request import Request,urlopen

FILES={'widget.json':65536,'icon.png':262144,'README.md':65536,'LICENSE':65536}
def get_json(url):
 headers={'User-Agent':'UltraBar-Store-Checks','Accept':'application/vnd.github+json'}
 token=os.environ.get('GH_TOKEN')
 if token:headers['Authorization']='Bearer '+token
 with urlopen(Request(url,headers=headers),timeout=20) as r:return json.load(r)

def validate_link(link,manifest,author,previous=None):
 if not isinstance(link,dict) or set(link)!={'repository','commit','release'}:raise ValueError('repository.json requires repository, commit and release.')
 repo=link['repository'];commit=link['commit'];release=link['release']
 if not isinstance(repo,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*',repo):raise ValueError('repository must be OWNER/REPO.')
 if not isinstance(commit,str) or not re.fullmatch(r'[a-f0-9]{40}',commit):raise ValueError('commit must be a full immutable commit SHA.')
 if not isinstance(release,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}',release):raise ValueError('release must be a versioned release tag.')
 if author.lower()!=repo.split('/')[0].lower():raise ValueError('Only the linked repository owner may submit or update this package. Organization repositories require maintainer handling.')
 if previous and previous['repository'].lower()!=repo.lower():raise ValueError('Repository ownership cannot be changed in an update. Request an explicit ownership transfer separately.')
 expected='https://github.com/'+repo+'/blob/'+commit+'/widget.json'
 if manifest.get('source')!=expected:raise ValueError('manifest.source must match repository.json commit and root widget.json.')
 return repo,commit,release

def run(root,trusted,pr):
 author=pr['user']['login'];errors=[];notes=[]
 base=trusted/'submissions';current=root/'submissions'
 for folder in sorted(current.iterdir()):
  if not folder.is_dir():continue
  old=base/folder.name
  changed=not old.exists() or any(not (old/f.name).exists() or f.read_bytes()!=(old/f.name).read_bytes() for f in folder.iterdir() if f.is_file()) or any(not (folder/f.name).exists() for f in old.iterdir() if f.is_file())
  if not changed:continue
  try:
   manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
   if not (folder/'repository.json').exists():
    # Existing first-party submissions remain compatible. Third parties cannot edit them.
    if old.exists() and author.lower()=='qlerup' and not (old/'repository.json').exists():
     notes.append(folder.name+': legacy first-party package; maintainer submission.');continue
    raise ValueError('Add repository.json linking your own public GitHub repository and release.')
   if old.exists() and not (old/'repository.json').exists():
    if author.lower()!='qlerup':raise ValueError('Only the maintainer can migrate a legacy package to its owner repository.')
   link=json.loads((folder/'repository.json').read_text());previous=json.loads((old/'repository.json').read_text()) if (old/'repository.json').exists() else None
   repo,commit,tag=validate_link(link,manifest,author,previous)
   if old.exists():
    prior=json.loads((old/'manifest.json').read_text())
    if prior['id']!=manifest['id']:raise ValueError('Keep the approved package ID.')
    from validate import valid_version
    if valid_version(manifest['version'])<=valid_version(prior['version']):raise ValueError('Updates must increase version.')
   metadata=get_json('https://api.github.com/repos/'+repo)
   if metadata.get('private') or metadata.get('archived') or metadata['full_name'].lower()!=repo.lower():raise ValueError('Repository must be public, active and at its canonical owner/name.')
   release=get_json('https://api.github.com/repos/'+repo+'/releases/tags/'+tag)
   if release.get('draft') or release.get('prerelease'):raise ValueError('Publish a stable GitHub release before submitting.')
   ref=get_json('https://api.github.com/repos/'+repo+'/git/ref/tags/'+tag)['object']
   for _ in range(5):
    if ref['type']=='commit':break
    if ref['type']!='tag':raise ValueError('Release tag does not resolve to a commit.')
    ref=get_json('https://api.github.com/repos/'+repo+'/git/tags/'+ref['sha'])['object']
   if ref['type']!='commit' or ref['sha']!=commit:raise ValueError('Release tag must point to the reviewed commit.')
   for name,limit in FILES.items():
    file=folder/name
    if file.is_symlink() or not file.is_file() or file.stat().st_size>limit:raise ValueError('Missing or invalid '+name)
    with urlopen(Request('https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+name,headers={'User-Agent':'UltraBar-Store-Checks'}),timeout=20) as r:raw=r.read(limit+1)
    if raw!=file.read_bytes():raise ValueError(name+' differs from the linked release source. Copy the exact reviewed bytes.')
   notes.append(folder.name+': repository owner, stable release commit and upstream files verified.')
  except Exception as exc:errors.append(folder.name+': '+str(exc))
 for folder in base.iterdir():
  if folder.is_dir() and not (current/folder.name).exists() and author.lower()!='qlerup':errors.append(folder.name+': only a Store maintainer can delist an approved package.')
 return errors,notes

if __name__=='__main__':
 result=Path(os.environ['STORE_RESULT'])
 checks=['Repository ownership and unchanged approved repository identity','Stable upstream release resolves to reviewed commit','Upstream widget, icon, README and license match reviewed bytes','Existing package ID and increasing update version']
 try:
  pr=get_json('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/pulls/'+os.environ['PR_NUMBER'])
  if pr['head']['sha']!=os.environ['REVIEW_SHA']:raise ValueError('PR changed during validation. Rerun checks.')
  errors,notes=run(Path(sys.argv[1]),Path(sys.argv[2]),pr)
 except Exception as exc:errors=[str(exc)];notes=[]
 data=json.loads(result.read_text()) if result.exists() else dict(ready=False,errors=['Package validation did not finish.'],notes=[],checks=[])
 data['errors']+=errors;data['notes']+=notes;data['checks']+=checks;data['ready']=not data['errors'] and bool(data['notes']);result.write_text(json.dumps(data),encoding='utf-8')
 print('\n'.join(errors+notes));sys.exit(bool(errors))
