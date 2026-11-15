"""Update one PR comment using only trusted checks; never execute PR code."""
import json,os,html
from pathlib import Path
from urllib.request import Request,urlopen

MARKER='<!-- ultrabar-store-check -->'


def render_comment(result,repo,run_id,sha=''):
    ready=result.get('ready',False)
    body=MARKER+'\n## '+('Automated checks passed' if ready else 'Changes needed before approval')+'\n\n'
    if sha:body+='Reviewed commit: <code>'+html.escape(sha)+'</code>\n\n'
    errors=result.get('errors',[])
    if errors:
        body+='### What to fix\n\n'
        for error in errors[:40]:
            item='<pre>'+html.escape(str(error)[:1800])+'</pre>\n\n'
            if len(body)+len(item)>45000:
                body+='More errors are listed in the full run log.\n\n';break
            body+=item
        if len(errors)>40:body+='More errors are listed in the full run log.\n\n'
        body+='Correct the listed files in your upstream app repository, rebuild/release when needed, then copy the matching files and updated release metadata into this PR. Do not edit the generated catalog.\n\n'
    elif ready:
        body+='All automated checks passed for this commit. New packages still require maintainer approval. Eligible existing-package updates are evaluated by the **Merge eligible package update** job under the existing policy.\n\n'
    else:
        body+='The validation run did not complete. Check the run log for a tooling or download failure and rerun; this is not an approval.\n\n'
    body+='### Automated check scope\n\n'
    body+='\n'.join('- '+html.escape(str(item)) for item in result.get('checks',[]))+'\n\n'
    if result.get('notes'):body+='### Details\n\n<pre>'+html.escape('\n'.join(result['notes']))[:7000]+'</pre>\n\n'
    body+='### Still needs testing\n\nStatic checks verify the supported Studio package/install/launch and declared settings API 1 contract. They do **not** run submitted apps or prove that the app starts successfully, that its features/custom settings work, that it is safe, or that redistribution rights are valid. Test install, launch, reading/applying settings, confirmation, restart persistence, update and removal on physical Core before approval. Apps need the documented settings API for editable fields; special provisioning remains a trusted integration.\n\n'
    body+='### Rerun\n\nPush fixes to this same PR branch; checks rerun automatically and update this comment. Maintainers can also use **Actions > Store submission checks > Run workflow** with the PR number.\n\n'
    body+='[Full run log](https://github.com/'+repo+'/actions/runs/'+run_id+') | [Submission guide](https://github.com/'+repo+'/blob/main/CONTRIBUTING.md) | [Settings requirements](https://github.com/'+repo+'/blob/main/APP-SETTINGS.md)'
    return body


def main():
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
    body=render_comment(r,repo,os.environ['GITHUB_RUN_ID'],expected)
    existing=None
    for page in range(1,11):
        comments=api('/issues/'+number+'/comments?per_page=100&page='+str(page))
        existing=next((c for c in comments if c['user']['login']=='github-actions[bot]' and c.get('body','').startswith(MARKER)),None)
        if existing or len(comments)<100:break
    if existing:api('/issues/comments/'+str(existing['id']),'PATCH',dict(body=body))
    else:api('/issues/'+number+'/comments','POST',dict(body=body))


if __name__=='__main__':main()
