"""Build the public catalog from per-package manifests; never execute package code."""
import json
from pathlib import Path
import re
import importlib.util

spec=importlib.util.spec_from_file_location('trusted_listing',Path(__file__).with_name('listing.py'))
listing=importlib.util.module_from_spec(spec);spec.loader.exec_module(listing)


def build(root):
    packages=[];seen=set()
    for folder in sorted((Path(root)/'submissions').iterdir()):
        if folder.is_symlink() or not folder.is_dir() or not re.fullmatch(r'[a-z0-9-]{1,80}',folder.name):
            raise ValueError('Invalid submission folder')
        path=folder/'manifest.json'
        if path.is_symlink() or path.stat().st_size>65536:raise ValueError('Invalid package manifest')
        entry=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(entry,dict) or not isinstance(entry.get('id'),str):raise ValueError('Missing package ID')
        if entry['id'] in seen:raise ValueError('Duplicate package ID')
        seen.add(entry['id']);packages.append(entry)
        if not listing.state(folder)['listed']:packages.pop()
        if len(seen)>500:raise ValueError('Too many packages')
    return dict(schemaVersion=1,packages=sorted(packages,key=lambda p:p['id']))


if __name__=='__main__':
    import sys
    Path(sys.argv[2]).write_bytes((json.dumps(build(Path(sys.argv[1])),indent=2)+'\n').encode())
