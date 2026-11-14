"""Trusted PR ownership and pinned upstream checks; submitted files are data only."""
import json,os,re,sys,hashlib,io,zipfile
from pathlib import Path
from urllib.request import Request,urlopen

FILES={'widget.json':65536,'icon.png':262144,'README.md':65536,'LICENSE':65536}
def get_json(url):
 headers={'User-Agent':'UltraBar-Store-Checks','Accept':'application/vnd.github+json'}
 token=os.environ.get('GH_TOKEN')
 if token:headers['Authorization']='Bearer '+token
 with urlopen(Request(url,headers=headers),timeout=20) as r:return json.load(r)

def validate_link(link,manifest,author,previous=None):
 if not isinstance(link,dict) or set(link) not in ({'repository','commit','release'},{'repository','commit','release','type'}):raise ValueError('repository.json requires repository, commit and release.')
 if 'type' in link and link['type']!=manifest.get('type'):raise ValueError('repository.json type must match manifest.json type.')
 repo=link['repository'];commit=link['commit'];release=link['release']
 if not isinstance(repo,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*',repo):raise ValueError('repository must be OWNER/REPO.')
 if not isinstance(commit,str) or not re.fullmatch(r'[a-f0-9]{40}',commit):raise ValueError('commit must be a full immutable commit SHA.')
 if not isinstance(release,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}',release):raise ValueError('release must be a versioned release tag.')
 if author.lower()!=repo.split('/')[0].lower():raise ValueError('Only the linked repository owner may submit or update this package. Organization repositories require maintainer handling.')
 if previous and previous['repository'].lower()!=repo.lower():raise ValueError('Repository ownership cannot be changed in an update. Request an explicit ownership transfer separately.')
 kind=manifest.get('type','corebar-widget')
 leaf={'corebar-widget':'widget.json','studio-plugin':'plugin.json','corebar-app':'AndroidManifest.xml'}.get(kind)
 if not leaf:raise ValueError('Unknown package type.')
 expected='https://github.com/'+repo+'/blob/'+commit+'/'+leaf
 if manifest.get('source')!=expected:raise ValueError('manifest.source must match repository.json commit and the source file for its package type.')
 return repo,commit,release

def run(root,trusted,pr):
 author=pr['user']['login'];errors=[];notes=[]
 changed=set()
 for parent in (root/'submissions',trusted/'submissions'):
  for folder in parent.iterdir():
   if not folder.is_dir():continue
   left=root/'submissions'/folder.name;right=trusted/'submissions'/folder.name
   def contents(path):return {str(f.relative_to(path)):f.read_bytes() for f in path.rglob('*') if f.is_file()} if path.exists() else None
   if contents(left)!=contents(right):changed.add(folder.name)
 if len(changed)>1:return ['One PR may change only one plugin package. Split these packages into separate PRs: '+', '.join(sorted(changed))],[]

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
    if author.lower()=='qlerup' and not (old/'repository.json').exists() and (old.exists() or manifest.get('id') in ('studio.drive.widget','studio.system.widget')):
     notes.append(folder.name+': legacy first-party package; maintainer submission.');continue
    raise ValueError('Add repository.json linking your own public GitHub repository and release.')
   if old.exists() and not (old/'repository.json').exists():
    if author.lower()!='qlerup':raise ValueError('Only the maintainer can migrate a legacy package to its owner repository.')
   link=json.loads((folder/'repository.json').read_text());previous=json.loads((old/'repository.json').read_text()) if (old/'repository.json').exists() else None
   if not old.exists() and 'type' not in link:raise ValueError('New registrations must declare type in repository.json, matching manifest.json.')
   repo,commit,tag=validate_link(link,manifest,author,previous)
   if old.exists():
    prior=json.loads((old/'manifest.json').read_text())
    if prior['id']!=manifest['id']:raise ValueError('Keep the approved package ID.')
    if prior['type']!=manifest['type']:raise ValueError('Updates must keep the approved package type.')
    def valid_version(value):
     if not isinstance(value,str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)',value):raise ValueError('Invalid version.')
     return tuple(map(int,value.split('.')))
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
   kind=manifest['type']
   files={k:v for k,v in FILES.items() if k!='widget.json'}
   if kind!='corebar-app':files['widget.json' if kind=='corebar-widget' else 'plugin.json']=65536
   for name,limit in files.items():
    file=folder/name
    if file.is_symlink() or not file.is_file() or file.stat().st_size>limit:raise ValueError('Missing or invalid '+name)
    with urlopen(Request('https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+name,headers={'User-Agent':'UltraBar-Store-Checks'}),timeout=20) as r:raw=r.read(limit+1)
    if raw!=file.read_bytes():raise ValueError(name+' differs from the linked release source. Copy the exact reviewed bytes.')
   if kind=='corebar-app':
    verify_apk_source(folder,repo,commit,tag)
    if old.exists() and prior.get('android',{}).get('signerSha256')!=manifest['android']['signerSha256']:raise ValueError('APK updates must keep the approved signing identity.')
    if old.exists() and (prior['android']['packageId']!=manifest['android']['packageId'] or prior['android']['versionCode']>=manifest['android']['versionCode']):raise ValueError('APK updates keep Android package ID and increase versionCode.')
   notes.append(folder.name+': repository owner, stable release commit and upstream files verified.')
  except Exception as exc:errors.append(folder.name+': '+str(exc))
 for folder in base.iterdir():
  if folder.is_dir() and not (current/folder.name).exists() and author.lower()!='qlerup':errors.append(folder.name+': only a Store maintainer can delist an approved package.')
 return errors,notes


def verify_apk_source(folder,repo,commit,tag):
 tree=get_json('https://api.github.com/repos/'+repo+'/git/trees/'+commit+'?recursive=1')
 if tree.get('truncated'):raise ValueError('Source tree is too large for review.')
 expected={x['path']:x for x in tree['tree'] if x['type']!='tree'}
 if len(expected)>256 or any(x['type']!='blob' or x['mode'] not in ('100644','100755') for x in expected.values()):raise ValueError('Source must be at most 256 regular tracked files; no submodules or symlinks.')
 archive=folder/'source.zip'
 if archive.is_symlink() or archive.stat().st_size>16*1024*1024:raise ValueError('Invalid source.zip.')
 with zipfile.ZipFile(archive) as z:
  names=z.namelist()
  if len(names)!=len(set(names)) or set(names)!=set(expected) or sum(i.file_size for i in z.infolist())>16*1024*1024:raise ValueError('source.zip must contain every tracked source file at repository root, exactly once, within 16 MiB.')
  for name in names:
   raw=z.read(name)
   if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=expected[name]['sha']:raise ValueError('Source archive differs from pinned Git commit: '+name)
 for name,limit in (('app.apk',256*1024*1024),('source.zip',16*1024*1024)):
  with urlopen(Request('https://github.com/'+repo+'/releases/download/'+tag+'/'+name,headers={'User-Agent':'UltraBar-Store-Checks'}),timeout=30) as r:raw=r.read(limit+1)
  if raw!=(folder/name).read_bytes():raise ValueError(name+' differs from upstream release asset.')

if __name__=='__main__':
 result=Path(os.environ['STORE_RESULT'])
 checks=['Repository ownership and unchanged approved repository identity','Stable upstream release resolves to reviewed commit','Upstream package, icon, README and license match reviewed bytes; APK source archive matches pinned Git tree','Existing package ID and increasing update version']
 try:
  pr=get_json('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/pulls/'+os.environ['PR_NUMBER'])
  if pr['head']['sha']!=os.environ['REVIEW_SHA']:raise ValueError('PR changed during validation. Rerun checks.')
  errors,notes=run(Path(sys.argv[1]),Path(sys.argv[2]),pr)
 except Exception as exc:errors=[str(exc)];notes=[]
 data=json.loads(result.read_text()) if result.exists() else dict(ready=False,errors=['Package validation did not finish.'],notes=[],checks=[])
 data['errors']+=errors;data['notes']+=notes;data['checks']+=checks;data['ready']=not data['errors'] and bool(data['notes']);result.write_text(json.dumps(data),encoding='utf-8')
 print('\n'.join(errors+notes));sys.exit(bool(errors))
