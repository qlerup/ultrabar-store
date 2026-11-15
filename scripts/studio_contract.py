"""Static Studio v1 contract checks. Submission files are read as data only."""
def manifest_issues(manifest):
    """Return independent, actionable problems instead of stopping at the first."""
    errors=[]
    def problem(field,message,fix):errors.append(f'manifest.json / {field}: {message} Fix: {fix}')
    if not isinstance(manifest,dict):return ['manifest.json: Expected a JSON object. Fix: copy a manifest example and fill its fields.']
    required={'schemaVersion','id','name','description','version','type','publisher','license','source','compatibility','permissions'}
    allowed=required|{'artifact','icon','android','settings'}
    for field in sorted(required-set(manifest)):problem(field,'Required field is missing.','Add '+field+' using CONTRIBUTING.md and manifest.schema.json.')
    for field in sorted(set(manifest)-allowed):problem(field,'Studio does not support this manifest field.','Remove it; custom settings, scripts and provisioning need a supported Studio integration, not extra manifest fields.')
    if type(manifest.get('schemaVersion')) is not int or manifest.get('schemaVersion')!=1:problem('schemaVersion','Unsupported manifest version.','Set schemaVersion to the integer 1.')
    for field in ('id','name','description','version','type','publisher','license','source'):
        if field in manifest and (not isinstance(manifest[field],str) or not manifest[field].strip()):problem(field,'Expected non-empty text.','Supply a non-empty string.')
    kind=manifest.get('type')
    if 'settings' in manifest:
        try:
            import importlib.util
            from pathlib import Path
            spec=importlib.util.spec_from_file_location('trusted_app_settings_contract',Path(__file__).with_name('app_settings_contract.py'))
            contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
            contract.validate_schema(manifest['settings'])
            if kind!='corebar-app':raise ValueError('settings belongs to corebar-app; native widgets use widget.json settings.')
            version=manifest.get('compatibility',{}).get('minStudioVersion','')
            if not isinstance(version,str) or not __import__('re').fullmatch(r'\d+\.\d+\.\d+',version) or tuple(map(int,version.split('.'))) < (0,45,0):raise ValueError('Settings API 1 requires minStudioVersion 0.45.0 or newer.')
        except (ValueError,AttributeError) as exc:problem('settings',str(exc),'Follow APP-SETTINGS.md and include the identical studio-settings.json in the source and APK assets.')
    if kind not in ('corebar-app','corebar-widget','studio-plugin'):problem('type','Unsupported package type.','Choose corebar-app, corebar-widget or studio-plugin.')
    compatibility=manifest.get('compatibility')
    if not isinstance(compatibility,dict):problem('compatibility','Expected a compatibility object.','Declare minStudioVersion, hostApi, models, lineosVersions and abis.')
    else:
        for field in sorted(set(compatibility)-{'minStudioVersion','hostApi','models','lineosVersions','abis'}):problem('compatibility.'+field,'Unsupported compatibility field.','Remove it and use the supported compatibility fields.')
        if type(compatibility.get('hostApi')) is not int or compatibility.get('hostApi')!=1:problem('compatibility.hostApi','Studio supports hostApi 1.','Set the integer 1 and use only its supported package features.')
        if not isinstance(compatibility.get('minStudioVersion'),str):problem('compatibility.minStudioVersion','Required Studio version is missing or not text.','Set a version such as "0.24.0"; declare at least the version implementing your features.')
        for field,values in (('models',{'CB01'}),('abis',{'armeabi-v7a'}),('lineosVersions',{'1.0.8','1.0.9'})):
            value=compatibility.get(field)
            if not isinstance(value,list) or not value or any(not isinstance(v,str) or v not in values for v in value) or len(value)!=len(set(v for v in value if isinstance(v,str))):
                problem('compatibility.'+field,'Missing, duplicate or unsupported compatibility declaration.','Declare a non-empty list of tested values from '+', '.join(sorted(values))+'. Current Studio/Core support is limited to this matrix.')
    permissions=manifest.get('permissions')
    if not isinstance(permissions,list) or any(not isinstance(p,str) for p in permissions) or (isinstance(permissions,list) and len({p for p in permissions if isinstance(p,str)})!=len(permissions)):
        problem('permissions','Expected a list of distinct permission names.','Use [] for JSON packages, or list the exact APK permissions once each.')
    elif kind in ('corebar-widget','studio-plugin') and permissions:problem('permissions','Declarative widgets cannot request Android permissions.','Set permissions to []. Use a corebar-app for Android executable code.')
    android=manifest.get('android')
    if kind=='corebar-app':
        if not isinstance(android,dict):problem('android','Android identity is required for APK installation.','Add packageId, versionCode, minSdk and signerSha256 from your signed release APK.')
        else:
            for field in sorted({'packageId','versionCode','minSdk','signerSha256'}-set(android)):problem('android.'+field,'Required Android metadata is missing.','Copy the value from your signed release APK.')
            for field in sorted(set(android)-{'packageId','versionCode','minSdk','signerSha256'}):problem('android.'+field,'Unsupported Android metadata field.','Remove this field; Studio does not interpret custom Android install/settings commands.')
            sdk=android.get('minSdk')
            if type(sdk) is not int or not 26<=sdk<=29:problem('android.minSdk','The supported CB01 Android runtime is API 29; Store APKs require minSdk 26 or later.','Build an APK with minSdk between 26 and 29 and test it on CB01. targetSdk may be higher; do not merely change manifest.json.')
    elif 'android' in manifest:problem('android','Android metadata belongs to corebar-app packages.','Remove android, or submit a signed APK using type corebar-app.')
    for field in ('artifact','icon'):
        if field in manifest:
            value=manifest[field]
            if not isinstance(value,dict) or set(value)!={'url','size','sha256'}:problem(field,'Download metadata needs exactly url, size and sha256.','Use metadata for the immutable official Store mirror; ask the maintainer to prepare it for a first submission.')
    return errors


def required_files(folder,manifest):
    """Report every missing required file before attempting dependent checks."""
    kind=manifest.get('type') if isinstance(manifest,dict) else None
    if not isinstance(kind,str):kind=None
    files=['README.md','LICENSE','icon.png']+{'corebar-app':['app.apk','source.zip'],'corebar-widget':['widget.json'],'studio-plugin':['plugin.json']}.get(kind,[])
    if isinstance(manifest,dict) and 'settings' in manifest:files.append('studio-settings.json')
    return [f'{name}: Required file is missing or a symlink. Fix: include the exact release file in this submission folder; see CONTRIBUTING.md.' for name in files if (folder/name).is_symlink() or not (folder/name).is_file()]
