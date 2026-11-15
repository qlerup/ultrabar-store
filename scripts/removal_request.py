"""Read issue form data, verify approved owner, and update a bot comment."""
import json,os,re,subprocess
from pathlib import Path


def verify(root,package_id,login):
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:\.[a-z][a-z0-9-]*)+',package_id):return False,'Invalid package ID.'
    for folder in (root/'submissions').iterdir():
        manifest=json.loads((folder/'manifest.json').read_text())
        if manifest['id']!=package_id:continue
        owner=json.loads((folder/'repository.json').read_text())['repository'].split('/')[0]
        return login.lower()==owner.lower(),('Registered repository owner verified.' if login.lower()==owner.lower() else 'Requester does not match the registered repository owner; maintainer review is required.')
    return False,'Package ID is not registered.'


def main():
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text());issue=event['issue']
    match=re.search(r'### Package ID\s+([^\s]+)',issue.get('body',''))
    package_id=match[1] if match else ''
    verified,message=verify(Path('.'),package_id,issue['user']['login'])
    marker='<!-- store-removal-request -->'
    text=marker+'\n## '+('Verified removal request' if verified else 'Removal request needs review')+'\n\n'+message+'\n\nNo package was removed. The Store maintainer can use **Actions > Remove or restore package**, enter the package ID and reason, then review and merge the generated PR. Existing installations and source repositories are preserved.'
    repo=os.environ['GITHUB_REPOSITORY'];number=str(issue['number'])
    def api(path,method='GET',body=None):
        args=['gh','api','repos/'+repo+path,'--method',method]
        if body is not None:args+=['--input','-']
        raw=subprocess.check_output(args,input=json.dumps(body).encode() if body is not None else None)
        return json.loads(raw)
    existing=api('/issues/'+number+'/comments?per_page=100')
    old=next((c for c in existing if c['user']['login']=='github-actions[bot]' and c['body'].startswith(marker)),None)
    api('/issues/comments/'+str(old['id']) if old else '/issues/'+number+'/comments','PATCH' if old else 'POST',dict(body=text))


if __name__=='__main__':main()
