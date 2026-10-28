"""Run statements recovered from rebuilt DATs against controlled JS game APIs."""
from pathlib import Path
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build import compile_source
from dat_codec import decode
def descend(block,*names):
    for name in names:block=next(e['value'] for e in block['entries'] if e['kind']=='block' and e['name']==name)
    return block
def blocks(block,path=''):
    for entry in block['entries']:
        if entry['kind']=='block':
            name=path+'.'+entry['name'] if path else entry['name']
            yield name,entry['value'];yield from blocks(entry['value'],name)
def flatten(block):
    return '\n'.join('{\n'+flatten(e['value'])+'\n}' if e['kind']=='block' else e['value'] for e in block['entries'])
def verify():
    files,_=compile_source();main=decode(files['CFG/Main.dat'],'blockpar')['root'];reports={}
    press=[b for p,b in blocks(main) if p.endswith('GraphButton.OnPressCode')];assert len(press)==1
    bootstrap=descend(main,'BV','OnLoad','FHDWormholeRuntimeBootstrap')
    for language in ['Rus','Eng']:
        lang=decode(files[f'CFG/{language}/Lang.dat'],'blockpar')['root']
        act=descend(lang,'ShipInfo','AddInfo','CustomInfos','FHDWormholeRuntime','OnActCode')
        scripts={name:re.sub(r'\b(?:int|float|str|dword|unknown)\s+(\w+)',r'var \1',flatten(block)).replace('exit;','return;')
                 for name,block in [('bootstrap',bootstrap),('press',press[0]),('act',act)]}
        fixture=(ROOT/'tests/behavior_fixture.js').read_text('utf-8').replace('SOURCE_SCRIPTS',json.dumps(scripts,ensure_ascii=False))
        result=subprocess.run(['node','-e',fixture],capture_output=True,text=True)
        assert result.returncode==0,result.stdout+'\n'+result.stderr
        reports[language]=json.loads(result.stdout)
    return {'kind':'JS-adapted compiled statements with controlled game API fixtures',
            'languages':reports,'live_game_executed':False,'native_generation_distribution_model_rerun':False}
if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False,indent=2))
