#!/usr/bin/env python3
"""Build Wormhole 0.7.4 without a previous release, game or prebuilt files."""
from pathlib import Path
import argparse,hashlib,json,platform,zipfile,zlib
from dat_codec import encode as encode_dat,decode as decode_dat
from gi_codec import encode as encode_gi,decode as decode_gi
ROOT=Path(__file__).resolve().parents[1]
PREFIX='Mods/FHD_MODS/FHD_Wormhole/'
def load(path):return json.loads(Path(path).read_text('utf-8'))
def sha(data):return hashlib.sha256(data).hexdigest()
def walk(block,path=''):
    for entry in block['entries']:
        name=path+'.'+entry['name'] if path else entry['name']
        if entry['kind']=='block':yield from walk(entry['value'],name)
        else:yield name,entry['value']
def compile_source(root=ROOT):
    source=root/'source';files={};configs={}
    for path in sorted((source/'CFG').rglob('*.json')):
        tree=load(path);data=encode_dat(tree);assert decode_dat(data,tree['format'])==tree
        name=path.relative_to(source).with_suffix('.dat').as_posix();files[name]=data;configs[name]=tree
    for path in sorted((source/'graphics').glob('*.json')):
        tree=load(path);data=encode_gi(tree);assert decode_gi(data)==tree
        files['DATA/FormShip2/'+path.stem+'.gi']=data
    files['ModuleInfo.txt']=(source/'ModuleInfo.txt').read_bytes().decode('utf-8').encode('cp1251')
    return files,configs
def resource_audit(files,configs):
    refs=[]
    for alias,value in walk(configs['CFG/CacheData.dat']['root']):
        path=value.replace('\\','/')
        if path.startswith(PREFIX):refs.append({'alias':alias,'present':path[len(PREFIX):] in files})
    return {'cache_references_checked':len(refs),'missing':[r for r in refs if not r['present']]}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--strict-original',action='store_true');args=parser.parse_args()
    files,configs=compile_source();expected=load(ROOT/'original-file-sha256.json')
    if set(files)!=set(expected):raise SystemExit('Runtime file list differs from upload')
    hashes={name:sha(data) for name,data in sorted(files.items())};changed=[name for name in hashes if hashes[name]!=expected[name]]
    if args.strict_original and changed:raise SystemExit('Original SHA-256 mismatch: '+repr(changed))
    audit=resource_audit(files,configs)
    if audit['missing']:raise SystemExit('Missing resources: '+repr(audit['missing']))
    out=ROOT/'dist';out.mkdir(exist_ok=True);archive=out/'FHD_Wormhole_v0.7.4_FROM_SOURCE.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(PREFIX+name,date_time=(2026,10,28,0,0,0));info.external_attr=0o644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    report={'runtime_files':len(files),'source_derived_files':len(files),'byte_identical_to_upload':not changed,
            'different_files':changed,'prebuilt_runtime_inputs_used':False,'previous_release_required':False,'game_required_for_build':False,
            'dat_files':4,'gi_files':6,'gi_type':0,'gi_pixel_format':'argb8888','dll_files':0,'scr_files':0,
            'resource_audit':audit,'sha256':hashes,'package_sha256':sha(archive.read_bytes()),
            'python':platform.python_version(),'zlib':zlib.ZLIB_RUNTIME_VERSION,'live_game_executed':False}
    (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(files)} runtime files built; {len(files)-len(changed)} original hashes match')
    print('No previous release, game installation or compiled mod files used')
    print('Package:',archive)
if __name__=='__main__':main()
