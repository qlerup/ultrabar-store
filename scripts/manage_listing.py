"""Maintainer-dispatched action creates a listing-only PR; never merges it."""
import json,os,re,subprocess
from pathlib import Path


def main():
    package_id=os.environ['PACKAGE_ID'];action=os.environ['LISTING_ACTION'];reason=os.environ['LISTING_REASON'].strip()
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:\.[a-z][a-z0-9-]*)+',package_id) or action not in ('remove','restore') or not 1<=len(reason)<=1000:raise ValueError('Invalid package ID, action or reason.')
    folders=[f for f in Path('submissions').iterdir() if json.loads((f/'manifest.json').read_text())['id']==package_id]
    if len(folders)!=1:raise ValueError('Package ID must identify one registered package.')
    folder=folders[0];repo=os.environ['GITHUB_REPOSITORY']
    if os.environ.get('LISTING_DRY_RUN')=='true':
        print('Dry run: '+action+' '+package_id+' using '+folder.as_posix()+'/listing.json. No branch, PR or catalog was changed.')
        return
    def api(path,method='GET',body=None):
        args=['gh','api','repos/'+repo+path,'--method',method]
        if body is not None:args+=['--input','-']
        raw=subprocess.check_output(args,input=json.dumps(body).encode() if body is not None else None)
        return json.loads(raw) if raw else None
    base=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()
    tree=api('/git/trees','POST',dict(base_tree=api('/git/commits/'+base)['tree']['sha'],tree=[dict(path=folder.as_posix()+'/listing.json',mode='100644',type='blob',content=json.dumps(dict(listed=action=='restore',reason=reason),indent=2)+'\n')]))
    title=('Remove ' if action=='remove' else 'Restore ')+package_id+' in Store'
    commit=api('/git/commits','POST',dict(message=title,tree=tree['sha'],parents=[base]))
    branch='maintenance/listing-'+os.environ['GITHUB_RUN_ID']+'-'+os.environ.get('GITHUB_RUN_ATTEMPT','1')
    api('/git/refs','POST',dict(ref='refs/heads/'+branch,sha=commit['sha']))
    pr=api('/pulls','POST',dict(title=title,head=branch,base='main',body='Maintainer-requested listing change.\n\nReason: '+reason+'\n\nOnly listing.json changes. Package source, registration and existing installations are preserved. Review and merge this PR to publish the change. This PR must not auto-merge.'))
    # PRs opened by GITHUB_TOKEN do not trigger normal PR workflows.
    api('/actions/workflows/validate.yml/dispatches','POST',dict(ref='main',inputs=dict(pr_number=str(pr['number']))))
    print(pr['html_url'])
    if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).write_text('Review the prepared listing change: '+pr['html_url']+'\n')


if __name__=='__main__':main()
