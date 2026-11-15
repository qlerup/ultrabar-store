"""Trusted data-only validator. Never imports or executes submitted code."""
import copy,hashlib,json,re,sys,os,io
from pathlib import Path
from types import SimpleNamespace
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlsplit
updates=SimpleNamespace(version_tuple=lambda v:tuple(map(int,v.split('.'))),UpdateError=ValueError)
ASSET_PREFIX='https://github.com/qlerup/ultrabar-store/releases/download/'
MAX_SIZE=256*1024*1024
ID=re.compile(r'[a-z][a-z0-9]*(?:\.[a-z][a-z0-9-]*)+')
ANDROID_ID=re.compile(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+')
HEX=re.compile(r'[a-f0-9]{64}')
class StoreError(ValueError):pass
class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != 'https' or parsed.hostname not in ('github.com','release-assets.githubusercontent.com','objects.githubusercontent.com','raw.githubusercontent.com') or parsed.username or parsed.password:
            raise StoreError('The package redirected outside the approved download hosts.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def valid_version(value):
    if not isinstance(value,str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)',value): raise StoreError('Invalid package version.')
    try: return updates.version_tuple(value)
    except updates.UpdateError as exc: raise StoreError('Invalid package version.') from exc

def validate_icon_metadata(icon):
    if not isinstance(icon,dict) or set(icon)!={'url','size','sha256'}:raise StoreError('An icon needs url, size and sha256.')
    url=icon['url']
    if not isinstance(url,str) or not url.startswith(ASSET_PREFIX) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*\.png',url[len(ASSET_PREFIX):]):raise StoreError('Icon must be a PNG asset in the official store repository.')
    if type(icon['size']) is not int or not 0<icon['size']<=262144 or not HEX.fullmatch(str(icon['sha256'])):raise StoreError('Invalid icon size or checksum.')

def validate_icon_bytes(raw,icon):
    from PIL import Image
    if len(raw)!=icon['size'] or hashlib.sha256(raw).hexdigest()!=icon['sha256']:raise StoreError('Icon checksum or size mismatch.')
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format!='PNG' or im.size not in ((256,256),(512,512)) or getattr(im,'n_frames',1)!=1:raise StoreError('Icon must be a static 256x256 or 512x512 PNG.')
            im.verify()
        with Image.open(io.BytesIO(raw)) as im:im.load()
    except StoreError:raise
    except Exception as exc:raise StoreError('Invalid PNG icon.') from exc
    return raw

def validate_entry(entry):
    if not isinstance(entry, dict): raise StoreError('Invalid catalog entry.')
    p = copy.deepcopy(entry)
    if p.get('schemaVersion') != 1 or not ID.fullmatch(str(p.get('id',''))): raise StoreError('Unsupported package manifest.')
    for field, maximum in [('name',100),('description',1000),('license',200)]:
        if not isinstance(p.get(field),str) or not 1 <= len(p[field]) <= maximum: raise StoreError('Incomplete package information.')
    valid_version(p.get('version'))
    if 'publisher' in p:
        owner=urlsplit(p.get('source','')).path.strip('/').split('/')[0]
        if not isinstance(p['publisher'],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}',p['publisher']) or p['publisher'].lower()!=owner.lower():raise StoreError('Publisher must match the source repository owner.')
    if p.get('type') not in ('corebar-app','studio-plugin','corebar-widget'): raise StoreError('Unknown package type.')
    compatibility=p.get('compatibility',{})
    valid_version(compatibility.get('minStudioVersion'))
    if type(compatibility.get('hostApi')) is not int: raise StoreError('Invalid host API.')
    for key in ('models','lineosVersions','abis'):
        values=compatibility.get(key,[])
        if not isinstance(values,list) or len(values)>32 or any(not isinstance(v,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,60}',v) for v in values): raise StoreError('Invalid compatibility declaration.')
    permissions=p.get('permissions')
    if not isinstance(permissions,list) or len(permissions)>100 or any(not isinstance(v,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.]{0,150}',v) for v in permissions): raise StoreError('Invalid permissions.')
    artifact=p.get('artifact',{})
    url=artifact.get('url','')
    if not isinstance(url,str) or not url.startswith(ASSET_PREFIX) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*',url[len(ASSET_PREFIX):]): raise StoreError('Package must be a versioned asset in the official store repository.')
    if type(artifact.get('size')) is not int or not 0 < artifact['size'] <= MAX_SIZE or not HEX.fullmatch(str(artifact.get('sha256',''))): raise StoreError('Invalid artifact checksum or size.')
    if p['type']=='corebar-app':
        android=p.get('android',{})
        if not ANDROID_ID.fullmatch(str(android.get('packageId',''))) or android['packageId'].startswith(('android.','com.android.','com.ultrabar.')): raise StoreError('Invalid or reserved Android package ID.')
        if type(android.get('versionCode')) is not int or android['versionCode']<1 or type(android.get('minSdk')) is not int or android['minSdk']<26 or not HEX.fullmatch(str(android.get('signerSha256',''))): raise StoreError('Invalid Android package metadata.')
    elif p['type'] in ('studio-plugin','corebar-widget') and permissions:
        raise StoreError('Declarative Studio plugins cannot request permissions.')
    return p

def plugin_templates(raw):
    try: data=json.loads(raw)
    except (ValueError,UnicodeError) as exc: raise StoreError('Invalid plugin JSON.') from exc
    if not isinstance(data,dict) or set(data)!={'pluginApi','widgets'} or data['pluginApi']!=1 or not isinstance(data['widgets'],list) or not 1<=len(data['widgets'])<=32: raise StoreError('Unsupported declarative plugin format.')
    result=[]
    for w in data['widgets']:
        if not isinstance(w,dict) or set(w)-{'name','kind','background','textColor','accent'}: raise StoreError('Plugins may contain widget presets only, not code or commands.')
        if not isinstance(w.get('name'),str) or not 1<=len(w['name'])<=100 or w.get('kind') not in ('clock','cpu','memory','gpu','disk'): raise StoreError('Invalid plugin widget.')
        for field in ('background','textColor','accent'):
            if field in w and not re.fullmatch(r'#[a-fA-F0-9]{6}',str(w[field])): raise StoreError('Invalid widget color.')
        result.append(dict(w))
    return result

def widget_package(raw):
    try:data=json.loads(raw)
    except (ValueError,UnicodeError) as exc:raise StoreError('Invalid widget package JSON.') from exc
    if not isinstance(data,dict) or set(data)!={'widgetApi','runtime','widgets'} or type(data['widgetApi']) is not int or data['widgetApi']!=1 or data['runtime']!='studio-native-v1':
        raise StoreError('Unsupported widget package runtime.')
    widgets=data['widgets']
    if not isinstance(widgets,list) or not 1<=len(widgets)<=32:raise StoreError('A package must contain 1-32 widgets.')
    result=[];ids=set()
    for w in widgets:
        if not isinstance(w,dict) or set(w)-{'id','name','kind','background','textColor','accent','hourFormat','showSeconds','showDate','kindOptions'}:raise StoreError('Unsupported widget field. Executable code is not supported.')
        key=w.get('id')
        if not isinstance(key,str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}',key) or key in ids:raise StoreError('Widget IDs must be unique.')
        ids.add(key)
        base={k:v for k,v in w.items() if k in ('name','kind','background','textColor','accent')}
        plugin_templates(json.dumps(dict(pluginApi=1,widgets=[base])).encode())
        if w.get('hourFormat','24') not in ('12','24') or any(type(w[k]) is not bool for k in ('showSeconds','showDate') if k in w):raise StoreError('Invalid clock settings.')
        if w['kind']!='clock' and any(k in w for k in ('hourFormat','showSeconds','showDate')):raise StoreError('Clock settings require a clock widget.')
        if 'kindOptions' in w:
            options=w['kindOptions']
            if not isinstance(options,list) or not 2<=len(options)<=3 or any(k not in ('cpu','memory','gpu') for k in options) or len(set(options))!=len(options) or w['kind'] not in options:
                raise StoreError('Choose 2-3 distinct CPU, RAM or GPU kinds including the default kind.')
        result.append(dict(w,_widgetPackage=True))
    return result



def read(path,limit=65536):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>limit:raise ValueError('Missing, oversized or symlink file: '+str(path.name))
    return path.read_bytes()

def validate_tree(root,verify_assets=False,generated_catalog=False):
    errors=[];notes=[];packages={}
    if generated_catalog:
        import importlib.util
        spec=importlib.util.spec_from_file_location('trusted_catalog',Path(__file__).with_name('build_catalog.py'))
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        catalog=builder.build(root)
    else:catalog=json.loads(read(root/'catalog.json',1024*1024))
    if not isinstance(catalog,dict) or catalog.get('schemaVersion')!=1 or not isinstance(catalog.get('packages'),list):raise ValueError('Invalid catalog')
    folders=list((root/'submissions').iterdir()) if (root/'submissions').exists() else []
    if len(folders)>500 or len(catalog['packages'])>500:raise ValueError('Too many submissions')
    for folder in folders:
        try:
            if folder.is_symlink() or not folder.is_dir() or not re.fullmatch(r'[a-z0-9-]{1,80}',folder.name):raise ValueError('Invalid submission folder')
            for name in ('README.md','LICENSE'):
                try:
                    if len(read(folder/name).strip())<20:raise ValueError(name+' is empty')
                except Exception as exc:errors.append(folder.name+': '+str(exc))
            manifest=json.loads(read(folder/'manifest.json'))
            for field in ('id','name','description','version','type','publisher','license','source','compatibility','permissions','schemaVersion'):
                if field not in manifest:raise ValueError('Missing manifest field '+field)
            if not re.fullmatch(r'https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(tree|blob)/[a-f0-9]{40}/[^\s]+',manifest['source']):raise ValueError('source must link to an exact GitHub source commit (40 hex digits)')
            kind=manifest['type'];widgets=[]
            filename={'corebar-widget':'widget.json','studio-plugin':'plugin.json','corebar-app':'app.apk'}.get(kind)
            if not filename:raise ValueError('Unknown package type')
            raw=read(folder/filename,MAX_SIZE if kind=='corebar-app' else 65536)
            if kind=='corebar-widget':widgets=widget_package(raw)
            elif kind=='studio-plugin':plugin_templates(raw)
            else:
                # Load only this trusted checkout's inspector, even with python -I.
                import importlib.util
                spec=importlib.util.spec_from_file_location('trusted_apk_check',Path(__file__).with_name('apk_check.py'))
                inspector=importlib.util.module_from_spec(spec);spec.loader.exec_module(inspector)
                inspector.inspect(folder/filename,manifest)
                read(folder/'source.zip',16*1024*1024)
            icon_raw=read(folder/'icon.png',262144)
            icon_meta=manifest.get('icon',dict(url=ASSET_PREFIX+'pending/icon.png',size=len(icon_raw),sha256=hashlib.sha256(icon_raw).hexdigest()))
            validate_icon_metadata(icon_meta);validate_icon_bytes(icon_raw,icon_meta)
            compat=manifest['compatibility']
            if compat.get('hostApi')!=1 or valid_version(compat['minStudioVersion'])<(0,20,0):raise ValueError('Widget packages require hostApi 1 and Studio 0.20.0+')
            if kind=='corebar-widget' and (compat.get('abis')!=['armeabi-v7a'] or compat.get('models')!=['CB01'] or not compat.get('lineosVersions') or not set(compat['lineosVersions'])<= {'1.0.8','1.0.9'}):raise ValueError('Declare tested CB01/ARM32/LineOS 1.0.8 or 1.0.9 compatibility')
            if any('kindOptions' in w for w in widgets) and valid_version(compat['minStudioVersion'])<(0,24,0):raise ValueError('Selectable measurements require Studio 0.24.0+')
            effective=copy.deepcopy(manifest)
            if 'artifact' not in effective:
                effective['artifact']=dict(url=ASSET_PREFIX+'pending/'+filename,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
                notes.append(folder.name+': submission valid; owner must publish the artifact before catalog approval.')
            validate_entry(effective)
            if effective['artifact']['size']!=len(raw) or effective['artifact']['sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Artifact hash/size does not match package file')
            if manifest['id'] in packages:raise ValueError('Duplicate package ID')
            packages[manifest['id']]=(manifest,raw,icon_raw)
        except Exception as exc:errors.append(folder.name+': '+str(exc))
    seen=set()
    for entry in catalog['packages']:
        try:
            validate_entry(entry)
            if entry['id'] in seen:raise ValueError('Duplicate catalog ID')
            seen.add(entry['id'])
            if entry['id'] not in packages:raise ValueError('Catalog entry has no valid submission')
            manifest,raw,icon_raw=packages[entry['id']]
            if 'icon' not in manifest:raise ValueError('Owner must publish icon.png and add its icon URL, size and SHA-256 before approval')
            validate_icon_metadata(manifest['icon'])
            if manifest!=entry or 'artifact' not in manifest:raise ValueError('Catalog must exactly match the published manifest')
            if verify_assets:
                req=Request(entry['artifact']['url'],headers={'User-Agent':'UltraBar-Store-Validator'})
                with build_opener(SafeRedirect).open(req,timeout=20) as response:
                    remote=response.read(entry['artifact']['size']+1)
                if remote!=raw:raise ValueError('Published GitHub asset differs from reviewed package')
                req=Request(manifest['icon']['url'],headers={'User-Agent':'UltraBar-Store-Validator'})
                with build_opener(SafeRedirect).open(req,timeout=20) as response:remote_icon=response.read(262145)
                if remote_icon!=icon_raw:raise ValueError('Published icon differs from reviewed icon.png')
                validate_icon_bytes(remote_icon,manifest['icon'])
            notes.append(entry['id']+': catalog and package checks passed; owner review and physical testing still required.')
        except Exception as exc:errors.append('catalog: '+str(exc))
    for package_id in packages:
        if package_id not in seen:
            import importlib.util
            spec=importlib.util.spec_from_file_location('trusted_listing',Path(__file__).with_name('listing.py'))
            listing=importlib.util.module_from_spec(spec);spec.loader.exec_module(listing)
            folder=next(f for f in folders if json.loads(read(f/'manifest.json'))['id']==package_id)
            if listing.state(folder)['listed']:errors.append(package_id+': awaiting owner publication: add the official release artifact and matching catalog entry before approval.')
            else:notes.append(package_id+': delisted; registration and local source retained.')
    return errors,notes

if __name__=='__main__':
    try:errors,notes=validate_tree(Path(sys.argv[1]),'--verify-assets' in sys.argv,'--generated-catalog' in sys.argv)
    except Exception as exc:errors=[str(exc)];notes=[]
    ready=not errors and bool(notes)
    checks=['Required files for declared type, manifest.json, icon.png, README.md and LICENSE','Manifest identity, semantic version, source commit and compatibility','Declarative runtime/settings or APK metadata, permissions and cryptographic signature','Unique package/widget IDs and exact catalog/manifest match','Static PNG icon: 256x256 or 512x512, at most 256 KiB, valid image data','Local SHA-256 and byte size','Published GitHub release bytes match reviewed package (when catalogued)']
    result=dict(ready=ready,errors=errors,notes=notes,checks=checks)
    if os.environ.get('STORE_RESULT'):Path(os.environ['STORE_RESULT']).write_text(json.dumps(result),encoding='utf-8')
    report='Store submission checks\n\n'+'\n'.join(['ERROR: '+e for e in errors]+notes or ['No packages submitted yet.'])+'\n'
    print(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        import html
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as output:output.write('<pre>'+html.escape(report)+'</pre>')
    sys.exit(bool(errors))
