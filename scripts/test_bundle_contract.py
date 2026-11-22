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

    def test_bundled_app_owned_panels_require_new_studio(self):
        from widget_studio_contract import legacy_bambu
        descriptor=dict(widgetApi=1,runtime='studio-native-v1',widgets=[dict(id='bambu-liquid',name='Bambu',kind='bambu',studio=legacy_bambu())])
        manifest=dict(type='corebar-app',bundledWidgets=descriptor,android=dict(packageId='dk.ultrabar.bambu'),compatibility=dict(minStudioVersion='0.46.0'))
        with self.assertRaisesRegex(ValueError,'0.49.0'):bundle_contract.validate(manifest,widget_package)
        manifest['compatibility']['minStudioVersion']='0.49.0'
        self.assertEqual(bundle_contract.validate(manifest,widget_package)[0]['studio'],legacy_bambu())

    def test_package_owned_provider_requires_matching_android_receiver(self):
        descriptor = dict(widgetApi=1, runtime='android-appwidget-v1',
                          widgets=[dict(id='clock', name='Clock', provider='Clock')])
        manifest = dict(type='corebar-app', bundledWidgets=descriptor,
                        compatibility=dict(minStudioVersion='0.52.18'))
        self.assertEqual(bundle_contract.validate(manifest, widget_package)[0]['provider'], 'Clock')
        with self.assertRaisesRegex(ValueError, '0.52.18'):
            bundle_contract.validate(dict(manifest, compatibility=dict(minStudioVersion='0.52.17')), widget_package)
        xml = """E: manifest
  E: application
    E: receiver
      A: android:name=".Clock"
      E: intent-filter
        E: action
          A: android:name="android.appwidget.action.APPWIDGET_UPDATE"
      E: meta-data
        A: android:name="android.appwidget.provider"
        A: android:resource=@0x7f010001"""
        bundle_contract.validate_providers(xml, descriptor, 'org.example')
        for changed in (xml.replace('.Clock', '.Other'), xml.replace('resource=', 'value='),
                        xml.replace('APPWIDGET_UPDATE', 'OTHER')):
            with self.assertRaisesRegex(ValueError, 'Clock'):
                bundle_contract.validate_providers(changed, descriptor, 'org.example')
