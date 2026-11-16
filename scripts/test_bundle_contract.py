import json,tempfile,unittest,zipfile
from pathlib import Path
from validate import widget_package
import bundle_contract,studio_contract

class BundleTests(unittest.TestCase):
    def test_one_apk_typed_templates_and_exact_embedded_descriptor(self):
        descriptor=dict(widgetApi=1,runtime='studio-native-v1',widgets=[dict(id='bambu-liquid',name='Bambu',kind='bambu')])
        manifest=dict(type='corebar-app',bundledWidgets=descriptor,android=dict(packageId='dk.ultrabar.bambu'),compatibility=dict(minStudioVersion='0.46.0'))
        self.assertEqual(bundle_contract.validate(manifest,widget_package)[0]['id'],'bambu-liquid')
        for bad in [dict(manifest,type='corebar-widget'),dict(manifest,android=dict(packageId='dk.other.app')),dict(manifest,compatibility=dict(minStudioVersion='0.45.0'))]:
            with self.assertRaises(ValueError):bundle_contract.validate(bad,widget_package)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'app.apk'
            with zipfile.ZipFile(path,'w') as z:z.writestr('assets/ultrabar-widgets.json',json.dumps(descriptor))
            bundle_contract.inspect_apk(path,manifest)
            with zipfile.ZipFile(path,'w') as z:z.writestr('assets/ultrabar-widgets.json','{}')
            with self.assertRaises(ValueError):bundle_contract.inspect_apk(path,manifest)
