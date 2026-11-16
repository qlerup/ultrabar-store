import json,unittest
from validate import widget_package,StoreError
from bambu_contract import DEFAULTS,validate

class BambuTests(unittest.TestCase):
    def parse(self,**options):
        w=dict(DEFAULTS,id='bambu-liquid',name='Bambu Liquid',kind='bambu');w.update(options)
        return widget_package(json.dumps(dict(widgetApi=1,runtime='studio-native-v1',widgets=[w])).encode())
    def test_sizes_and_fields(self):
        for size in range(2,6):self.assertEqual(self.parse(expandedSlots=size)[0]['expandedSlots'],size)
    def test_bounds_types_and_no_code(self):
        for key,value in [('expandedSlots',True),('expandedSlots',0),('expandedSlots',6),('expandedSlots',2.5),('primary','camera'),('secondary','exec'),('showControls','yes'),('script','bad()')]:
            with self.subTest(key=key,value=value),self.assertRaises(StoreError):self.parse(**{key:value})
    def test_other_renderers_cannot_use_printer_settings(self):
        with self.assertRaises(ValueError):validate(dict(kind='clock',primary='progress'))
