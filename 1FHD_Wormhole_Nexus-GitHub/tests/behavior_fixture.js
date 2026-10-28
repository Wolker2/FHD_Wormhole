const assert=require('node:assert/strict');const scripts=SOURCE_SCRIPTS;
let checks=0;const check=(value,message)=>{assert(value,message);checks++;};
const constants={t_Hull:1000,t_Engine:1001,t_FuelTanks:1002};
const item=(type,name='ordinary',fields={})=>({type,name,special:-1,module:-1,series:-1,extra:[],durability:100,used:true,breakable:true,...fields});
function world(){
 const w={hull:0,engine:0,tank:0,items:[],form:'Ship',normal:true,now:100,order:0,target:1,
  pick:{order:7,target:2},confirm:true,infos:new Map(),states:new Map(),messages:[],lookups:0,
  additions:0,inventoryReads:0,forced:0,orderData:0,events:[]};
 const definitions={FHD_WormholeV2_Core:101,FHD_WormholeV2_EngineCore:102,
  FHD_WormholeV2_EngineTier41:103,FHD_WormholeV2_EngineTier82:104,
  FHD_WormholeV2_EngineExtra0:105,FHD_WormholeV2_EngineExtra41:106,FHD_WormholeV2_EngineExtra82:107};
 const resolve=name=>typeof name==='number'?[...w.infos.values()].find(x=>x.id===name):w.infos.get(name);
 const api={...constants,Player:()=>w,CurrentForm:()=>w.form,CurTurn:()=>w.now,
  FindBonusByCustomTag:tag=>{w.lookups++;return definitions[tag]??-1;},FindSeriesByName:()=>{w.lookups++;return 301;},
  ShipFindCustomShipInfoByType:(p,name)=>w.infos.has(name)?w.infos.get(name).id:-1,
  ShipAddCustomShipInfo:(p,name)=>{assert(!w.infos.has(name));const info={id:w.additions++,values:new Map()};w.infos.set(name,info);return info.id;},
  ShipCustomShipInfoData:(p,name,key,value)=>{const info=resolve(name);if(!info)return 0;if(value!==undefined)info.values.set(key,value);return info.values.get(key)||0;},
  ShipEqInSlot:(p,type)=>type===1000?w.hull:type===1001?w.engine:w.tank,
  HullSeries:x=>x.series,EqSpecial:x=>x.special,EqModule:x=>x.module,
  ItemExtraSpecialsCountByType:(x,id)=>x.extra.includes(id)?1:0,
  Name:x=>x.name,SetName:(x,name)=>x.name=name,lowercase:s=>s.toLowerCase(),findsubstr:(s,q)=>s.indexOf(q),
  InterfaceState:(form,name,value)=>w.states.set(name,value),
  CT:name=>name,MessageBox:text=>w.messages.push(text),MessageBoxYesNo:()=>w.confirm,
  ShipInNormalSpace:()=>w.normal,ShipOrder:()=>w.order,ShipOrderObj:()=>w.target,
  RunChildForm:name=>{assert.equal(name,'Galaxy');w.events.push('pick');w.order=w.pick.order;w.target=w.pick.target;},
  ShipItems:(p,index)=>{w.inventoryReads++;return index===undefined?w.items.length:w.items[index];},
  ItemIsInUse:x=>x.used,ItemType:x=>x.type,ItemCanBeBroken:x=>x.breakable,
  ItemDurability:(x,value)=>{if(value!==undefined)x.durability=value;return x.durability;},
  ShipOrderData1:(p,value)=>{w.orderData=value;w.events.push('order-data');},
  ForceNextDay:()=>{w.forced++;w.events.push('next-day');}};
 w.run=name=>new Function(...Object.keys(api),scripts[name])(...Object.values(api));
 w.ready=value=>{w.infos.get('FHDWormholeRuntime').values.set(1,value);};
 w.cooldown=()=>w.infos.get('FHDWormholeRuntime').values.get(1)||0;
 w.run('bootstrap');return w;
}
let w=world();check(w.additions===4,'four hidden service infos initialized');check(w.lookups===8,'definition caches initialized');
w.run('bootstrap');check(w.additions===4,'repeat bootstrap does not duplicate infos');
w.form='Galaxy';w.run('act');check(w.states.size===0,'UI callback exits outside Ship');
w.form='Ship';let lookups=w.lookups;w.run('act');check(w.states.get('FHDWormholeButton')===0,'no WH equipment hides button');
check(w.lookups===lookups&&w.inventoryReads===0,'UI callback does not scan definitions or inventory');
for(const fields of [{series:301},{special:101},{extra:[101]}]){
 w=world();w.hull=item(1000,'Hull',fields);w.run('act');check(w.states.get('FHDWormholeButton')===1,'new/legacy hull recognition');
 check(w.hull.name.includes('[WH/ЧВ]'),'recognized hull labeled');
}
for(const fields of [{module:102},{special:102},{extra:[102]},...Array.from({length:5},(_,i)=>({special:103+i}))]){
 w=world();w.engine=item(1001,'Engine',fields);w.run('act');check(w.states.get('FHDWormholeButton')===1,'new/legacy/tier/extra engine recognition');
 check(w.inventoryReads===0,'recognition only examines equipped items');
}
w=world();w.hull=item(1000,'ЧВ корпус',{series:301});w.run('act');check(w.hull.name==='ЧВ корпус','existing Cyrillic tag preserved case-insensitively');
w.hull=item(1000,'Fake [WH]');w.run('act');check(w.states.get('FHDWormholeButton')===0,'name alone does not fake WH capability');
w=world();w.infos.get('FHDWormholeRuntime').values.set(2,0);w.hull=item(1000,'Hull',{series:301});w.run('act');
check(w.states.get('FHDWormholeButton')===0&&w.inventoryReads===0,'missing cached core hides UI safely');
function equipped(){const x=world();x.hull=item(1000,'Hull',{series:301});return x;}
for(const reason of ['none','space','cooldown','cancel','no-pick','same-pick']){
 w=equipped();if(reason==='none')w.hull=0;if(reason==='space')w.normal=false;
 if(reason==='cooldown')w.ready(101);if(reason==='cancel')w.confirm=false;
 if(reason==='no-pick')w.pick={order:0,target:2};if(reason==='same-pick'){w.order=7;w.target=2;w.pick={order:7,target:2};}
 const before=w.cooldown();w.run('press');check(w.forced===0&&w.cooldown()===before,'rejected/cancelled jump has no cooldown/day effect: '+reason);
 check(w.inventoryReads===0,'rejected jump does not traverse equipment: '+reason);
}
w=equipped();w.engine=item(1001,'Engine');w.tank=item(1002,'Tank');
const weapon=item(1003,'Weapon'),artifact=item(999,'Artifact'),unused=item(1003,'Unused',{used:false}),solid=item(1003,'Unbreakable',{breakable:false});
w.items=[w.hull,w.engine,w.tank,weapon,artifact,unused,solid];w.run('press');
check(weapon.durability===1,'ordinary installed equipment critically worn');
check(w.engine.durability===10&&w.tank.durability===10,'engine and tank limited to 10');
check(w.hull.durability===100&&artifact.durability===100&&unused.durability===100&&solid.durability===100,'hull/artifact/unused/unbreakable preserved');
check(w.cooldown()===130&&w.states.get('FHDWormholeLock')===1,'shared cooldown set to current turn plus 30');
check(w.orderData===1&&w.forced===1&&w.events.join(',')==='pick,order-data,next-day','jump handoff sequence');
w.hull=0;w.engine.special=102;w.now=129;w.run('press');check(w.forced===1,'switching from hull to engine cannot bypass cooldown');
w.now=130;w.engine.durability=3;w.tank.durability=5;w.pick.target=3;w.run('press');
check(w.forced===2&&w.cooldown()===160,'jump allowed at cooldown boundary');
check(w.engine.durability===3&&w.tank.durability===5,'wear never repairs already lower durability');
w.run('act');check(w.states.get('FHDWormholeLock')===1,'lock shown while recharging');
w.now=160;w.run('act');check(w.states.get('FHDWormholeLock')===0,'lock hidden at cooldown boundary');
console.log(JSON.stringify({checks_passed:checks,game_api:'controlled fixtures',live_game_executed:false}));
