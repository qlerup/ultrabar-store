"""One reviewed APK may supply declarative templates for trusted native renderers."""
import json,zipfile
import importlib.util
from pathlib import Path

_panel_spec = importlib.util.spec_from_file_location(
    'trusted_widget_studio_contract', Path(__file__).with_name('widget_studio_contract.py'))
_panel = importlib.util.module_from_spec(_panel_spec)
_panel_spec.loader.exec_module(_panel)

def validate(manifest,parse):
    if 'bundledWidgets' not in manifest:return []
    if manifest.get('type')!='corebar-app':raise ValueError('bundledWidgets requires a corebar-app package.')
    if tuple(map(int,manifest.get('compatibility',{}).get('minStudioVersion','0.0.0').split('.')))<(0,46,0):raise ValueError('Bundled native widgets require Studio 0.46.0+.')
    descriptor=manifest['bundledWidgets']
    if not isinstance(descriptor,dict):raise ValueError('bundledWidgets must be a widget.json object.')
    templates=parse(json.dumps(descriptor).encode())
    if descriptor.get('runtime') == 'android-appwidget-v1' and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0, 52, 18):
        raise ValueError('Android widget providers require Studio 0.52.18+.')
    if _panel.requires_notification_runtime(templates) and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0, 52, 35):
        raise ValueError('Widget notifications and bell sounds require Studio 0.52.35 or newer.')
    if any(preset.get('images') for w in templates for preset in w.get('studio', {}).get('presentation', {}).get('presets', [])) and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0,52,24):
        raise ValueError('Package image presets require Studio 0.52.24+.')
    if any(w.get('kind')=='scene' or 'sounds' in w.get('studio',{}) or 'expanded' in w.get('studio',{}).get('layout',{}) or any(isinstance(v,dict) for v in w.get('studio',{}).get('layout',{}).values()) for w in templates) and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0,52,23):
        raise ValueError('Package panels and sounds require Studio 0.52.23+.')
    if any('sideTemperatures' in preset.get('nozzleGrid', {}) for w in templates for preset in w.get('studio', {}).get('presentation', {}).get('presets', [])) and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0,52,22):
        raise ValueError('Side temperature boxes require Studio 0.52.22+.')
    if any('nozzleGrid' in preset for w in templates for preset in w.get('studio', {}).get('presentation', {}).get('presets', [])) and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0,52,21):
        raise ValueError('Nozzle grid dimensions require Studio 0.52.21+.')
    if any(w.get('studio', {}).get('api') == 2 for w in templates) and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0,52,18):
        raise ValueError('Package-defined widget settings require Studio 0.52.18+.')
    if any('splitFlap' in p for w in templates for p in w.get('studio', {}).get('presentation', {}).get('presets', [])) and tuple(map(int, manifest['compatibility']['minStudioVersion'].split('.'))) < (0, 52, 17):
        raise ValueError('Split-flap displays require Studio 0.52.17+.')
    if any('sizes' in w for w in templates) and tuple(map(int,manifest['compatibility']['minStudioVersion'].split('.')))<(0,52,0):
        raise ValueError('Widget sizes require Studio 0.52.0 or newer.')
    if any('presentation' in w.get('studio',{}) for w in templates) and tuple(map(int,manifest['compatibility']['minStudioVersion'].split('.')))<(0,51,0):
        raise ValueError('Package-owned presentation presets require Studio 0.51.0 or newer.')
    if any('studio' in w for w in templates) and tuple(map(int,manifest['compatibility']['minStudioVersion'].split('.')))<(0,49,0):
        raise ValueError('App-owned Studio panels require Studio 0.49.0 or newer.')
    if any(w['kind']=='bambu' for w in templates) and manifest.get('android',{}).get('packageId')!='dk.ultrabar.bambu':
        raise ValueError('The Bambu renderer requires its fixed dk.ultrabar.bambu companion.')
    return templates

def inspect_apk(path,manifest):
    with zipfile.ZipFile(path) as archive:
        matches=[i for i in archive.infolist() if i.filename=='assets/ultrabar-widgets.json']
        if not matches and 'bundledWidgets' not in manifest:return None
        if len(matches)!=1 or matches[0].file_size>128*1024:raise ValueError('APK requires one bounded assets/widget.json descriptor.')
        descriptor=json.loads(archive.read(matches[0]))
        if 'bundledWidgets' in manifest and descriptor!=manifest['bundledWidgets']:raise ValueError('APK widget descriptor differs from its recorded bundle.')
        return descriptor

def validate_providers(xml, descriptor, package_id):
    """Check the widget declaration against receivers in the compiled APK."""
    if not descriptor or descriptor.get('runtime') != 'android-appwidget-v1':
        return
    import re
    from xml.etree.ElementTree import Element, SubElement
    root = Element('dump')
    stack = [(-1, root)]
    for line in xml.splitlines():
        element = re.match(r'(\s*)E: ([\w-]+)', line)
        if element:
            indent = len(element[1])
            while stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, SubElement(stack[-1][1], element[2])))
            continue
        attr = re.match(r'\s*A: android:([\w-]+)(?:\(0x[0-9a-f]+\))?=(?:"([^"]*)"|(\S+.*))', line)
        if attr:
            stack[-1][1].set(attr[1], attr[2] if attr[2] is not None else attr[3])
    available = set()
    for receiver in root.findall('./manifest/application/receiver'):
        name = receiver.get('name', '')
        if name.startswith('.'):
            name = package_id + name
        elif '.' not in name:
            name = package_id + '.' + name
        if receiver.get('enabled') == '(type 0x12)0x0':
            continue
        if receiver.find("./intent-filter/action[@name='android.appwidget.action.APPWIDGET_UPDATE']") is None:
            continue
        metadata = receiver.find("./meta-data[@name='android.appwidget.provider']")
        if metadata is not None and re.fullmatch(r'@0x[0-9a-fA-F]+', metadata.get('resource', '')):
            available.add(name)
    for widget in descriptor['widgets']:
        if package_id + '.' + widget['provider'] not in available:
            raise ValueError('Missing Android widget provider declaration for ' + widget['provider'])
