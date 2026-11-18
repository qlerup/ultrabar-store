"""Approve and queue only a verified update to one already approved owner package."""
import json
import os
from pathlib import Path
import re
import subprocess


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def changed_files(root, base, head):
    changes = git(root, 'diff', '--raw', '-z', '--no-renames', base, head).split(b'\0')
    paths = []
    for metadata, path in zip(changes[0:-1:2], changes[1:-1:2]):
        old_mode, new_mode = metadata.split()[:2]
        if old_mode[1:] not in (b'000000', b'100644', b'100755') or new_mode not in (b'100644', b'100755'):
            raise ValueError('Removed file, symbolic link or submodule.')
        paths.append(path.decode())
    return paths


def eligibility(base, submitted, author, paths):
    def load(root, name):return json.loads((root/name).read_text(encoding='utf-8'))
    folders={p.split('/')[1] for p in paths if p.startswith('submissions/') and len(p.split('/'))>=3}
    if len(folders)!=1:return False, 'Manual approval: one existing package is required.'
    folder=next(iter(folders));prefix='submissions/'+folder+'/'
    if any(not p.startswith(prefix) or '/' in p[len(prefix):] for p in paths):
        return False, 'Manual approval: changes outside the package. The catalog is generated automatically.'
    try:
        old=load(base,prefix+'manifest.json');new=load(submitted,prefix+'manifest.json')
        previous=load(base,prefix+'repository.json');link=load(submitted,prefix+'repository.json')
    except (OSError,ValueError):return False, 'Manual approval: new package or unregistered legacy package.'
    allowed={'manifest.json','repository.json','icon.png','README.md','LICENSE'}
    allowed|={'app.apk','source.zip','studio-settings.json'} if new.get('type')=='corebar-app' else {'widget.json','make_icon.py'} if new.get('type')=='corebar-widget' else {'plugin.json','make_icon.py'}
    if new.get('type')=='corebar-app' and new.get('bundledWidgets'):allowed.add('widget.json')
    if any(p[len(prefix):] not in allowed for p in paths):
        return False, 'Manual approval: unexpected package file.'
    if old.get('settings')!=new.get('settings'):return False, 'Manual approval: app settings contract changed.'
    if new.get('type')=='corebar-widget':
        def panels(root):
            path=root/prefix/'widget.json'
            if not path.exists():return {}
            return {w['id']:w['studio'] for w in json.loads(path.read_text(encoding='utf-8')).get('widgets',[]) if 'studio' in w}
        try:
            if panels(base)!=panels(submitted):return False, 'Manual approval: native app Studio panel contract changed.'
        except (OSError,ValueError,KeyError,TypeError):return False, 'Manual approval: invalid native app Studio panel.'

    if old.get('bundledWidgets')!=new.get('bundledWidgets'):return False,'Manual approval: bundled widget contract changed.'
    for key in ('id','type','publisher','permissions','compatibility','license'):
        if key not in old or old[key]!=new.get(key):return False, 'Manual approval: changed '+key+'.'
    repo=previous.get('repository','')
    if not repo or repo.lower()!=link.get('repository','').lower() or author.lower()!=repo.split('/')[0].lower() or author.lower()!=new['publisher'].lower():
        return False, 'Manual approval: owner or repository changed.'
    if link.get('type')!=new['type'] or previous.get('type')!=old['type']:
        return False, 'Manual approval: changed or missing registered package type.'
    def version(v):
        if not isinstance(v,str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)',v):raise ValueError()
        return tuple(map(int,v.split('.')))
    try:
        if version(new['version'])<=version(old['version']):return False, 'Manual approval: version did not increase.'
    except (KeyError,ValueError):return False, 'Manual approval: invalid version.'
    if old['type']=='corebar-app':
        for key in ('packageId','signerSha256','minSdk'):
            if old['android'][key]!=new.get('android',{}).get(key):return False, 'Manual approval: Android identity or requirements changed.'
        if new['android']['versionCode']<=old['android']['versionCode']:return False, 'Manual approval: Android versionCode did not increase.'
    return True, 'Existing package update from its registered owner; all package checks passed.'


def main():
    import sys
    base,submitted=map(Path,sys.argv[1:3]);repo=os.environ['GITHUB_REPOSITORY'];number=os.environ['PR_NUMBER']
    if not number.isdigit():raise ValueError('Invalid PR number')
    def api(path,method='GET',body=None):
        args=['gh','api','repos/'+repo+path,'--method',method]
        if body is not None:args+=['--input','-']
        raw=subprocess.check_output(args,input=json.dumps(body).encode() if body is not None else None)
        return json.loads(raw) if raw else None
    pr=api('/pulls/'+number)
    head=os.environ['REVIEW_SHA'];base_sha=os.environ['REVIEW_BASE_SHA']
    if pr['state']!='open' or pr['draft'] or pr['base']['ref']!='main' or pr['head']['sha']!=head or pr['base']['sha']!=base_sha:
        print('Manual approval or rerun: PR state, head or base changed.');return
    if git(base,'rev-parse','HEAD').decode().strip()!=base_sha or git(submitted,'rev-parse','HEAD').decode().strip()!=head:
        raise ValueError('Checked out commits differ from validation.')
    # Compare the exact trees, including file modes: symlinks/submodules never qualify.
    try:
        paths = changed_files(submitted, base_sha, head)
    except ValueError as error:
        print(f'Manual approval: {error}');return
    ready,message=eligibility(base,submitted,pr['user']['login'],paths)
    print(message)
    if not ready:return
    if 'store-manual-review' in [label['name'] for label in pr.get('labels',[])]:
        print('Manual approval requested by label.');return
    reviews=api('/pulls/'+number+'/reviews?per_page=100')
    latest={}
    for review in reviews:
        if review['state'] in ('APPROVED','CHANGES_REQUESTED','DISMISSED'):latest[review['user']['login']]=review['state']
    if 'CHANGES_REQUESTED' in latest.values():
        print('Manual approval: a reviewer requested changes.');return
    # Approval is pinned to the exact commit validated by the preceding job.
    if not any(r['user']['login']=='github-actions[bot]' and r['state']=='APPROVED' and r.get('commit_id')==head for r in reviews):
        api('/pulls/'+number+'/reviews','POST',dict(event='APPROVE',commit_id=head,body='Automatic approval: existing registered-owner update, unchanged identity/permissions/compatibility, and all Store checks passed.'))
    subprocess.run(['gh','pr','merge',number,'--repo',repo,'--auto','--squash','--match-head-commit',head],check=True)
    print('Automatic merge requested; GitHub still requires green checks and an up-to-date branch.')


if __name__=='__main__':main()
