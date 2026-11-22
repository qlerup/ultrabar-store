"""Synchronize one eligible Store update so the trusted validator can recheck it."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

from auto_update import changed_files, eligibility, git


def api(repo, path, *args):
    return json.loads(subprocess.check_output(['gh', 'api', f'repos/{repo}/{path}', *args]))


def candidate_tree(root, base, head, author):
    result = subprocess.run(
        ['git', 'merge-tree', '--write-tree', base, head], cwd=root, capture_output=True, check=False,
    )
    if result.returncode == 1:
        return None  # Git reported a merge conflict.
    result.check_returncode()
    tree = result.stdout.decode().strip()
    try:
        paths = changed_files(root, base, tree)
    except ValueError:
        return None
    if not paths:
        return None
    with tempfile.TemporaryDirectory() as directory:
        checkout = Path(directory) / 'candidate'
        git(root, 'worktree', 'add', '--quiet', '--detach', '--no-checkout', str(checkout), base)
        try:
            git(checkout, 'read-tree', '--reset', '-u', tree)
            return tree if eligibility(root, checkout, author, paths)[0] else None
        except (KeyError, TypeError, ValueError):
            return None  # Invalid submission data is handled by the normal PR validator.
        finally:
            git(root, 'worktree', 'remove', '--force', str(checkout))


def main():
    repo = os.environ['GITHUB_REPOSITORY']
    root = Path.cwd()
    base = git(root, 'rev-parse', 'HEAD').decode().strip()
    fields = 'number,isDraft,isCrossRepository,mergeStateStatus,reviewDecision,labels,statusCheckRollup'
    pulls = json.loads(subprocess.check_output([
        'gh', 'pr', 'list', '--repo', repo, '--base', 'main', '--limit', '1000', '--json', fields,
    ]))
    for pull in sorted(pulls, key=lambda item: item['number']):
        if (pull['isDraft'] or pull['reviewDecision'] == 'CHANGES_REQUESTED'
                or pull['mergeStateStatus'] in ('DIRTY', 'DRAFT')
                or any(label['name'] == 'store-manual-review' for label in pull['labels'])):
            continue
        number = pull['number']
        path = f'pulls/{number}'
        current = api(repo, path)
        if current['base']['sha'] != base:
            print('Main advanced during selection. The next run will use the new base.')
            return
        if (current['state'] != 'open' or current['draft'] or current['base']['ref'] != 'main'
                or any(label['name'] == 'store-manual-review' for label in current['labels'])):
            continue
        git(root, 'fetch', '--quiet', '--no-tags', 'origin', f'refs/pull/{number}/head')
        head = git(root, 'rev-parse', 'FETCH_HEAD').decode().strip()
        if head != current['head']['sha']:
            continue
        tree = candidate_tree(root, base, head, current['user']['login'])
        if tree is None:
            continue
        if git(root, 'merge-base', base, head).decode().strip() == base:
            # Skip a known failing head so other verified updates can proceed.
            checks = pull.get('statusCheckRollup') or []
            if any(check.get('name') == 'Validate package' and check.get('conclusion') in
                   ('FAILURE', 'TIMED_OUT', 'ACTION_REQUIRED') for check in checks):
                continue
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
                print(f"number={number}\nhead={head}\nbase={base}", file=output)
            print(f'Validating current PR #{number} against main.')
            return
        if pull['isCrossRepository'] and not current.get('maintainer_can_modify'):
            continue
        api(repo, f'{path}/update-branch', '--method', 'PUT', '-f', f'expected_head_sha={head}')
        for _ in range(15):
            time.sleep(2)
            updated = api(repo, path)
            if updated['head']['sha'] == head:
                continue
            if updated['base']['sha'] != base:
                print(f'Main advanced while synchronizing PR #{number}.')
                return
            commit = api(repo, f"git/commits/{updated['head']['sha']}")
            if commit['tree']['sha'] != tree or [parent['sha'] for parent in commit['parents']] != [head, base]:
                print(f'PR #{number} changed during synchronization. Its new head requires normal validation.')
                return
            with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
                print(f"number={number}\nhead={commit['sha']}\nbase={base}", file=output)
            print(f'Synchronized PR #{number}.')
            return
        raise RuntimeError(f'GitHub did not finish synchronizing PR #{number} in time.')
    print('No eligible Store update needs synchronization.')


if __name__ == '__main__':
    main()
