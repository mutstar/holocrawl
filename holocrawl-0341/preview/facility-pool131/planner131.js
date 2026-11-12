(function(root){'use strict';
 function random(key){let h=2166136261;for(const c of key)h=Math.imul(h^c.charCodeAt(0),16777619);return()=>{h+=0x6D2B79F5;let t=h;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};}
 function floors(){const out=[];for(let i=1;i<=14;i++)out.push({id:'JP-main-'+i,region:'JP',label:'잔향도시 '+i+'층'});out.push({id:'ID-entry',region:'ID',label:'ID 진입 구역'});for(let a=1;a<=3;a++)for(let f=1;f<=2;f++)out.push({id:`ID-${a}-${f}`,region:'ID',label:`ID 분기${a} · ${f}층`});out.push({id:'EN-entry',region:'EN',label:'EN 진입 구역'});for(let a=1;a<=6;a++)for(let f=1;f<=2;f++)out.push({id:`EN-${a}-${f}`,region:'EN',label:`EN 이계${a} · ${f}층`});return out;}
 function generate(registry,seed,{includePlanned=false}={}){
  const pool=registry.facilities.filter(f=>f.randomPoolMember!==false&&(includePlanned||f.status==='built')).slice().sort((a,b)=>a.id.localeCompare(b.id)),remaining=pool.map(f=>f.id),r=random(String(seed)+':shared-facilities131'),slots=[];
  for(const floor of floors()){const hit=r()<registry.policy.chancePerEligibleFloor;let facilityId=null;if(hit&&remaining.length)facilityId=remaining.splice(Math.floor(r()*remaining.length),1)[0];slots.push({...floor,facilityId,reason:facilityId?'selected':hit?'pool-exhausted':'chance-skip'});}
  return{version:131,seed:String(seed),mode:includePlanned?'future-all-planned':'built-only',poolSnapshot:pool.map(f=>f.id),slots,remaining,guaranteed:guaranteed(registry),placementConfirmed:false};
 }
 function guaranteed(registry){return(registry.guaranteedFacilities||[]).map(f=>({floorId:f.floorId,facilityId:f.id,chance:1}));}
 const api={generate,floors,guaranteed};root.SharedFacility131=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(globalThis);
