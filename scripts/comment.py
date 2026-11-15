"""Update one PR comment using only the trusted validator result."""
import json,os,html
from pathlib import Path
from urllib.request import Request,urlopen
number=os.environ.get('PR_NUMBER','')
if not number.isdigit():raise SystemExit('A numeric PR number is required.')
repo=os.environ['GITHUB_REPOSITORY']
base='https://api.github.com/repos/'+repo
headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','User-Agent':'UltraBar-Store-Checks'}
def api(path,method='GET',body=None):
    req=Request(base+path,headers=headers,method=method,data=json.dumps(body).encode() if body is not None else None)
    with urlopen(req,timeout=20) as r:return json.load(r)
pr=api('/pulls/'+number)
expected=os.environ.get('REVIEW_SHA','')
if expected and pr['head']['sha']!=expected:raise SystemExit('A newer commit exists; leaving its review comment untouched.')
p=Path(os.environ['STORE_RESULT'])
r=json.loads(p.read_text()) if p.exists() else dict(ready=False,errors=['The automated run did not finish. Inspect the Actions log and rerun it.'],notes=[],checks=[])
marker='<!-- ultrabar-store-check -->'
body=marker+'\n## '+('Ready for approval' if r['ready'] else 'Not ready for approval')+'\n\n'
body+='### Checks performed\n\n'+'\n'.join('- '+x for x in r['checks'])+'\n\n'
if r['errors']:
    body+='### Fixes needed\n\n<pre>'+html.escape('\n'.join(r['errors']))+'</pre>\n\n'
else:body+='All automated checks passed for this commit. Existing registered-owner updates are now evaluated for automatic approval and merge. New packages, registration migrations and identity/permission/requirement changes still require owner acceptance. See the Merge eligible package update job for the decision.\n\n'
if r['notes']:body+='### Details\n\n<pre>'+html.escape('\n'.join(r['notes']))+'</pre>\n\n'
body+='### Rerun\n\nPush fixes to this same PR branch; checks rerun automatically. Maintainers can also open Actions > Store submission checks > Run workflow and enter this PR number. This comment is updated on each run.\n\n'
body+='The bot validates package data and downloads; it does not test visual quality, hardware behavior or license ownership. Review those before merging.\n\n'
body+='[Full run log](https://github.com/'+repo+'/actions/runs/'+os.environ['GITHUB_RUN_ID']+') ? [Submission guide](https://github.com/'+repo+'/blob/main/CONTRIBUTING.md)'
existing=None
for page in range(1,11):
    comments=api('/issues/'+number+'/comments?per_page=100&page='+str(page))
    existing=next((c for c in comments if c['user']['login']=='github-actions[bot]' and c.get('body','').startswith(marker)),None)
    if existing or len(comments)<100:break
if existing:api('/issues/comments/'+str(existing['id']),'PATCH',dict(body=body))
else:api('/issues/'+number+'/comments','POST',dict(body=body))
