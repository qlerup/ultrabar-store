import json
from pathlib import Path
import subprocess
import tempfile
import unittest

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
