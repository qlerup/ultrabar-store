"""Store listing state is separate from immutable package/release metadata."""
import json


def state(folder):
    path=folder/'listing.json'
    if not path.exists():return dict(listed=True)
    if path.is_symlink() or path.stat().st_size>8192:raise ValueError('Invalid listing.json')
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict) or set(value)!={'listed','reason'} or type(value['listed']) is not bool or not isinstance(value['reason'],str) or not 1<=len(value['reason'].strip())<=1000:
        raise ValueError('listing.json requires listed (boolean) and reason (1-1000 characters).')
    return value
