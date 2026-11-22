"""Installed Android packages own their AppWidgetProvider and per-card settings."""
import json
import re
import importlib.util
from pathlib import Path
_settings_spec = importlib.util.spec_from_file_location('provider_settings',Path(__file__).with_name('app_settings_contract.py'))
_settings = importlib.util.module_from_spec(_settings_spec)
_settings_spec.loader.exec_module(_settings)
validate_schema = _settings.validate_schema

RUNTIME = 'android-appwidget-v1'
CLASS = re.compile(r'(?:[A-Za-z][A-Za-z0-9_]*\.)*[A-Za-z][A-Za-z0-9_]*')


def templates(data):
    if set(data) != {'widgetApi', 'runtime', 'widgets'} or type(data['widgetApi']) is not int or data['widgetApi'] != 1 or data['runtime'] != RUNTIME:
        raise ValueError('Invalid Android widget descriptor.')
    rows = data['widgets']
    if not isinstance(rows, list) or not 1 <= len(rows) <= 32:
        raise ValueError('Declare between one and 32 Android widget providers.')
    result, seen = [], set()
    for row in rows:
        if not isinstance(row, dict) or set(row) - {'id', 'name', 'provider', 'settings', 'sizes', 'feeds', 'inheritSettings'}:
            raise ValueError('Unsupported Android widget field.')
        key, name, provider = (row.get(k) for k in ('id', 'name', 'provider'))
        if not isinstance(key, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', key) or key in seen:
            raise ValueError('Android widget keys must be unique.')
        if not isinstance(name, str) or not name.strip() or len(name) > 100:
            raise ValueError('Invalid Android widget name.')
        if not isinstance(provider, str) or len(provider) > 180 or not CLASS.fullmatch(provider):
            raise ValueError('Use a provider class relative to the signed application package.')
        sizes = row.get('sizes', ['large', 'small'])
        if not isinstance(sizes, list) or not 1 <= len(sizes) <= 2 or any(s not in ('large','small') for s in sizes) or len(set(sizes)) != len(sizes):
            raise ValueError('Invalid Android widget sizes.')
        feeds = row.get('feeds', [])
        if not isinstance(feeds,list) or len(feeds)>2 or any(f not in ('pc.drives','pc.system') for f in feeds) or len(set(feeds))!=len(feeds):
            raise ValueError('Unsupported PC widget feed.')
        if 'settings' in row:
            validate_schema(row['settings'])
        inherit = row.get('inheritSettings', {})
        fields = {f['key'] for f in row.get('settings', {}).get('fields', [])}
        if not isinstance(inherit,dict) or not set(inherit) <= fields or any(not isinstance(v,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}',v) for v in inherit.values()):
            raise ValueError('Invalid widget setting migration.')
        seen.add(key)
        result.append(dict(row, kind='androidWidget', sizes=sizes, _widgetPackage=True))
    return result

