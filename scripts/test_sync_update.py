import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sync_update

from sync_update import candidate_tree


class SynchronizeUpdateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.org')
        self.git('config', 'user.name', 'Store test')
        self.package = self.root / 'submissions' / 'weather'
        self.package.mkdir(parents=True)
        self.manifest = {
            'id': 'alice.weather', 'publisher': 'alice', 'type': 'corebar-widget',
            'permissions': [], 'compatibility': {}, 'license': 'MIT', 'version': '1.0.0',
        }
        self.write_manifest()
        (self.package / 'repository.json').write_text(json.dumps({
            'repository': 'alice/weather', 'type': 'corebar-widget',
        }), encoding='utf-8')
        self.initial = self.commit('Initial Store')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args]).decode().strip()

    def write_manifest(self):
        (self.package / 'manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def commit(self, message):
        self.git('add', '.'); self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')

    def test_older_update_is_evaluated_against_merged_tree(self):
        (self.root / 'README.md').write_text('New Store documentation', encoding='utf-8')
        base = self.commit('Changes on main')
        self.git('checkout', '--detach', '-q', self.initial)
        self.manifest['version'] = '1.0.1'
        self.write_manifest()
        head = self.commit('Update package')
        self.git('checkout', '--detach', '-q', base)
        tree = candidate_tree(self.root, base, head, 'alice')
        self.assertIsNotNone(tree)
        self.assertEqual(self.git('show', f'{tree}:README.md'), 'New Store documentation')
        self.assertIsNone(candidate_tree(self.root, base, head, 'unregistered'))

    def test_conflict_requires_manual_resolution(self):
        self.manifest['version'] = '1.0.2'
        self.write_manifest()
        base = self.commit('Merge another update')
        self.git('checkout', '--detach', '-q', self.initial)
        self.manifest['version'] = '1.0.1'
        self.write_manifest()
        head = self.commit('Conflicting package update')
        self.git('checkout', '--detach', '-q', base)
        self.assertIsNone(candidate_tree(self.root, base, head, 'alice'))

    def test_serial_queue_selects_oldest_then_updates_next_against_new_main(self):
        from contextlib import ExitStack
        base = self.initial
        self.manifest['version'] = '1.0.1'
        self.write_manifest()
        first = self.commit('First widget update')
        self.git('checkout', '--detach', '-q', base)
        other = self.root / 'submissions' / 'another'
        import shutil
        shutil.copytree(self.package, other)
        base = self.commit('Register a second package')
        self.git('merge', '--no-edit', first)
        first = self.git('rev-parse', 'HEAD')
        self.git('checkout', '--detach', '-q', base)
        other_manifest = json.loads((other / 'manifest.json').read_text())
        other_manifest.update(version='1.1.0')
        (other / 'manifest.json').write_text(json.dumps(other_manifest))
        second = self.commit('Second widget update')
        self.git('checkout', '--detach', '-q', base)
        pulls = [dict(number=n,isDraft=False,isCrossRepository=False,mergeStateStatus='BLOCKED',
                      reviewDecision='REVIEW_REQUIRED',labels=[],statusCheckRollup=[]) for n in (2,1)]
        heads = {1:first,2:second}
        real_git = sync_update.git
        events = []
        def fake_git(root,*args):
            if args[0]=='fetch':
                n=int(args[-1].split('/')[2])
                return real_git(root,'fetch','--quiet','.',heads[n])
            return real_git(root,*args)
        def api(repo,path,*args):
            if path.startswith('git/commits/'):
                return dict(sha=heads[2],tree=dict(sha=self.git('rev-parse',heads[2]+'^{tree}')),parents=[dict(sha=second),dict(sha=base)])
            n=int(path.split('/')[1])
            if path.endswith('/update-branch'):
                events.append(n)
                self.git('checkout','--detach','-q',heads[n])
                self.git('merge','--no-edit',base)
                heads[n]=self.git('rev-parse','HEAD')
                self.git('checkout','--detach','-q',base)
            return dict(base=dict(sha=base,ref='main'),head=dict(sha=heads[n]),state='open',draft=False,labels=[],user=dict(login='alice'))
        output=self.root/'queue-output'
        # Mock only the GitHub listing, while keeping all local Git operations real.
        original_output = subprocess.check_output
        def cli(args,*a,**kw):
            if args[:3]==['gh','pr','list']:return json.dumps(pulls).encode()
            return original_output(args,*a,**kw)
        with ExitStack() as stack:
            stack.enter_context(patch.dict('os.environ',GITHUB_REPOSITORY='owner/store',GITHUB_OUTPUT=str(output)))
            stack.enter_context(patch.object(sync_update.Path,'cwd',return_value=self.root))
            stack.enter_context(patch.object(sync_update,'git',side_effect=fake_git))
            stack.enter_context(patch.object(sync_update,'api',side_effect=api))
            stack.enter_context(patch.object(sync_update.time,'sleep'))
            stack.enter_context(patch.object(subprocess,'check_output',side_effect=cli))
            sync_update.main()
            self.assertIn('number=1',output.read_text())
            self.assertEqual(events,[])
            pulls.pop()
            base=first
            self.git('checkout','--detach','-q',base)
            output.unlink()
            sync_update.main()
            self.assertEqual(events,[2])
            self.assertIn('base='+first,output.read_text())
            self.assertIn('head='+heads[2],output.read_text())
