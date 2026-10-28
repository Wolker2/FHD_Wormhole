from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile,unittest,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
from build import compile_source,resource_audit,load,PREFIX,walk
from gi_codec import encode,decode
from verify_behavior import verify,descend,blocks

def values(block):return {e['name']:e['value'] for e in block['entries'] if e['kind']=='parameter'}
class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.files,cls.configs=compile_source()
    def test_all_hashes_and_resource_paths(self):
        self.assertEqual({name:hashlib.sha256(data).hexdigest() for name,data in self.files.items()},load(ROOT/'original-file-sha256.json'))
        self.assertEqual(len(self.files),11)
        self.assertEqual(resource_audit(self.files,self.configs),{'cache_references_checked':6,'missing':[]})
    def test_native_definitions_and_event_contracts(self):
        main=self.configs['CFG/Main.dat']['root']
        self.assertFalse(any('ScriptLibs' in path for path,_ in blocks(main)))
        self.assertFalse(any('ImportedFunction(' in value for _,value in walk(main)))
        boot=descend(main,'BV','OnLoad','FHDWormholeRuntimeBootstrap')
        start=values(descend(main,'BV','OnStart','0DayScripts'))['FHDWormholeRuntimeBootstrap']
        self.assertEqual(''.join(e['value'] for e in boot['entries']),start)
        for language in ['Rus','Eng']:
            lang=self.configs[f'CFG/{language}/Lang.dat']['root']
            hull=values(descend(lang,'HullType','FHD_WormholeSeries'))
            self.assertEqual((hull['Probability'],hull['Race'],hull['ShipType']),('7','Any','Any'))
            for original,priority in [('FHD_WormholeV2_EngineCore',0),('FHD_WormholeV2_EngineTier41',41),('FHD_WormholeV2_EngineTier82',82)]:
                one=descend(lang,'MicroModuls',original);extra=descend(lang,'MicroModuls','FHD_WormholeV2_EngineExtra'+str(priority))
                self.assertEqual([(e['name'],e['value']) for e in one['entries'] if e['name']!='CustomTag'],[(e['name'],e['value']) for e in extra['entries'] if e['name']!='CustomTag'])
                props=values(extra);self.assertEqual((props['Priority'],props['Special'],props['OnPlanets'],props['Ruins']),(str(priority),'1','0','Any'))
            runtime=descend(lang,'ShipInfo','AddInfo','CustomInfos','FHDWormholeRuntime');props=values(runtime)
            self.assertNotIn('t_OnStep',props['OnActCodeTypes']);self.assertNotIn('OnActStepTypes',props)
            callback=''.join(value for _,value in walk(descend(runtime,'OnActCode')))
            for token in ['for(','while(','FindBonusByCustomTag','FindSeriesByName','GalaxySectors','PlanetItems','ShipItems(']:self.assertNotIn(token,callback)
    def test_behavior_in_both_localizations(self):
        result=verify()
        self.assertEqual({key:value['checks_passed'] for key,value in result['languages'].items()},{'Rus':53,'Eng':53})
    def test_argb_pixel_edit_is_used(self):
        for path in (ROOT/'source/graphics').glob('*.json'):
            source=load(path);self.assertEqual(source['layers'][0]['pixel_format'],'argb8888')
            source['layers'][0]['pixels'][0]^=1
            self.assertEqual(decode(encode(source)),source,path.name)
    def test_config_source_edit_is_used(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder);shutil.copytree(ROOT/'source',target/'source')
            path=target/'source/CFG/Rus/Lang.json';tree=load(path);block=descend(tree['root'],'HullType','FHD_WormholeSeries')
            next(e for e in block['entries'] if e['name']=='Probability')['value']='8'
            path.write_text(json.dumps(tree,ensure_ascii=False),encoding='utf-8');files,_=compile_source(target)
        self.assertEqual([name for name in files if files[name]!=self.files[name]],['CFG/Rus/Lang.dat'])
    def test_isolated_build_without_previous_release_or_binaries(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)
            for name in ['source','scripts']:shutil.copytree(ROOT/name,target/name,ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(ROOT/'original-file-sha256.json',target/'original-file-sha256.json')
            self.assertFalse(any(p.suffix.lower() in ['.dat','.gi','.dll','.exe','.scr'] for p in target.rglob('*') if p.is_file()))
            result=subprocess.run([sys.executable,str(target/'scripts/build.py'),'--strict-original'],cwd=target,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            with zipfile.ZipFile(target/'dist/FHD_Wormhole_v0.7.4_FROM_SOURCE.zip') as archive:
                self.assertEqual(len(archive.namelist()),11);self.assertIsNone(archive.testzip())
                for name,data in self.files.items():self.assertEqual(archive.read(PREFIX+name),data)
if __name__=='__main__':unittest.main()
