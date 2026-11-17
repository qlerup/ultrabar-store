"""The Store accepts only app-owned UI for approved runtime capabilities."""
import copy
import hashlib
import json
import unittest
import widget_studio_contract as panels
from validate import widget_package, StoreError
import test_validator as fixtures


class PanelTests(unittest.TestCase):
    def clock(self):
        return dict(api=1,settings=dict(api=1,fields=[dict(key='showSeconds',label='Seconds',type='boolean',default=True)]))

    def parse(self, descriptor):
        widget=dict(id='clock',name='Clock',kind='clock',studio=descriptor)
        return widget_package(json.dumps(dict(widgetApi=1,runtime='studio-native-v1',widgets=[widget])).encode())

    def test_app_owned_labels_defaults_and_help_are_retained(self):
        descriptor=self.clock();descriptor['help']='Package-provided help'
        self.assertEqual(self.parse(descriptor)[0]['studio'],descriptor)
        self.assertEqual(panels.validate(panels.legacy_bambu(),'bambu'),panels.legacy_bambu())

    def test_unsupported_code_runtime_fields_sources_and_provider_are_rejected(self):
        for descriptor in (dict(self.clock(),script='run()'),dict(self.clock(),sources={'showSeconds':'https://example.com'})):
            with self.assertRaises(StoreError):self.parse(descriptor)
        value=self.clock();value['settings']['fields'][0]['key']='arbitraryCommand'
        with self.assertRaises(StoreError):self.parse(value)
        value=panels.legacy_bambu();value['connection']['provider']='custom-plugin'
        with self.assertRaises(ValueError):panels.validate(value,'bambu')
        value=panels.legacy_bambu();value['connection']['fields'][3]['type']='string'
        with self.assertRaises(ValueError):panels.validate(value,'bambu')

    def test_measurement_choices_cannot_escape_package_kind_options(self):
        descriptor=dict(api=1,settings=dict(api=1,fields=[dict(key='kind',label='Show',type='choice',default='cpu',options=[dict(value='cpu',label='CPU'),dict(value='gpu',label='GPU')])]))
        widget=dict(id='monitor',name='Monitor',kind='cpu',kindOptions=['cpu','memory'],studio=descriptor)
        raw=json.dumps(dict(widgetApi=1,runtime='studio-native-v1',widgets=[widget])).encode()
        with self.assertRaisesRegex(StoreError,'measurement options'):widget_package(raw)

    def test_dynamic_choices_are_bound_to_the_pc_drive_capability(self):
        descriptor=dict(api=1,sources={'drive':'pc.drives'},settings=dict(api=1,fields=[dict(key='drive',label='Drive',type='string',maxLength=128,default='all')]))
        self.assertEqual(panels.validate(descriptor,'disk'),descriptor)
        for kind in ('clock','bambu'):
            with self.assertRaises(ValueError):panels.validate(descriptor,kind)


class PanelVersionTests(unittest.TestCase):
    def test_native_panel_requires_minimum_studio_version(self):
        fixture=fixtures.Checks('test_draft_submission_needs_owner_publication');fixture.setUp();self.addCleanup(fixture.doCleanups)
        self.raw,self.folder,self.manifest,self.root,self.save=fixture.raw,fixture.folder,fixture.manifest,fixture.root,fixture.save
        value=json.loads(self.raw);value['widgets'][0]['studio']=PanelTests().clock()
        self.raw=json.dumps(value).encode();(self.folder/'widget.json').write_bytes(self.raw)
        self.manifest['artifact']=dict(url='https://github.com/qlerup/ultrabar-store/releases/download/v1/widget.json',size=len(self.raw),sha256=hashlib.sha256(self.raw).hexdigest())
        self.save()
        from validate import validate_tree
        errors,_=validate_tree(self.root,generated_catalog=True)
        self.assertTrue(any('0.49.0' in error for error in errors),errors)
        self.manifest['compatibility']['minStudioVersion']='0.49.0';self.save()
        self.assertEqual(validate_tree(self.root,generated_catalog=True)[0],[])
